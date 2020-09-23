package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
	"sort"
	"strings"
)

//A struct representing a Playlist in Spotify https://developer.spotify.com/documentation/web-api/reference/playlists/
type Playlist struct {
	user string
	name string
	uri string
	tracks []string
	ref []string
}

//A Drainlist is simply a playlist which references other playlists to add songs from,
//might change this implementation to have a third structure allowing us to differentiate between songs removed in sources vs songs
//removed by the user...
type Drainlist struct {
	backing	*Playlist
	sources []*Playlist
}

//gets all playlists for the current user
func getPlaylists(accessToken string, client clientFacade, urlOffset string) []Playlist {
	spotUrl := "https://api.spotify.com/v1/me/playlists"
	if urlOffset != "" {
		spotUrl = urlOffset
	}

	headers := map[string]string{"Authorization":"Bearer " + accessToken}

	req := createRequest().withURL(spotUrl).withHeaders(headers).withMethod("GET").build()

	b, _ := client.Do(req)

	dest := make(map[string]interface{})

	err := json.Unmarshal(b, &dest)
	if err != nil {
		panic(err)
	}
	items := dest["items"].([]interface{})

	retList := make([]Playlist, 0)

	for _,v := range items {
		plist := v.(map[string]interface{})
		list := Playlist{
			user:user,
			name:plist["name"].(string),
			uri:plist["uri"].(string),

			tracks:nil,
			ref:nil,
		}
		retList = append(retList, list)
	}
	var next string
	if dest["next"] != nil { //check next is not null
		next = dest["next"].(string) //cast to string since something is there
		if next != "" { //recurse
			retList = append(retList, getPlaylists(accessToken, client, next)...)
		}
	}
	return retList
}

//for a given playlist get all tracks
func getTracks(accessToken string, client *clientFacade, urlOffset string, playlist *Playlist) []string{

	playlistId := uri2id(playlist.uri)
	_ = make([]string,0)
	spoturl :=  "https://api.spotify.com/v1/playlists/" + playlistId + "/tracks"
	if urlOffset != "" {
		spoturl = urlOffset
	}

	headers :=  map[string]string {"Authorization": "Bearer " + accessToken}

	req := createRequest().withURL(spoturl).withHeaders(headers).withMethod("GET").build()

	b, _ := (*client).Do(req)


	dest := make(map[string]interface{})

	err := json.Unmarshal(b, &dest)
	if err != nil {
		panic(err)
	}
	uris := make([]string, 0)
	items := dest["items"].([]interface{})
	for s := range items {
		d := items[s].(map[string]interface{})["track"].(map[string]interface{})["uri"].(string)
		uris = append(uris, d)
	}

	var next string
	if dest["next"] != nil { //check next is not null
		next = dest["next"].(string) //cast to string since something is there
		if next != "" { //recurse
			uris = append(uris, getTracks(accessToken, client, next, playlist)...)
		}
	}
	return uris

}

//add the listed tracks to the given playlist
func addTracks(accessToken string, client *clientFacade, trackUris []string, playlist *Playlist) error {
	spoturl := "https://api.spotify.com/v1/playlists/" + uri2id(playlist.uri) + "/tracks"

	headers := map[string]string{"Authorization":"Bearer " + accessToken}

	body := map[string][]string{
		"uris" : trackUris,
	}

	req := createRequest().withURL(spoturl).withHeaders(headers).withBodyJson(body).withMethod("POST").build()


	b, _ := (*client).Do(req)

	resp := string(b)

	if !strings.Contains(resp, "snapshot") {
		return errors.New("error incorrect response\n" + resp)
	}
	return nil
}

//remove the listed tracks from the given playlist
func removeTracks(accessToken string, client *clientFacade, trackUris []string, playlist *Playlist) error {
	spoturl := "https://api.spotify.com/v1/playlists/" + uri2id(playlist.uri) + "/tracks"

	headers := map[string]string{"Authorization":"Bearer " + accessToken, "Content-Type":"application/json"}
	bodyMap := make([]map[string]string, 0)

	for i := range trackUris {
		tMap := make(map[string]string)
		tMap["uri"] = trackUris[i]
		bodyMap = append(bodyMap, tMap)

	}

	body := map[string][]map[string]string{
		"tracks" : bodyMap,
	}

	bd, _ := json.Marshal(body)
	base, _ := http.NewRequest("DELETE", spoturl, bytes.NewReader(bd))

	req := factoryRequest(*base).withHeaders(headers).build()

	b, _ := (*client).Do(req)

	resp := string(b)
	if !strings.Contains(resp, "snapshot") {
		return errors.New("error incorrect response\n" + resp)
	}
	return nil
}

//creates a new playlist for the current user under the provided name
func createPlaylist(accessToken string, client *clientFacade, name string) (string, error) {

	userId, _ := getUserID(accessToken, client)
	spoturl := "https://api.spotify.com/v1/users/" + userId + "/playlists"

	headers := map[string]string{"Authorization":"Bearer " + accessToken, "Content-Type":"application/json"}
	body := map[string]string{
		"name" : name,
	}
	bd, _ := json.Marshal(body)
	base, _ := http.NewRequest("POST", spoturl, bytes.NewReader(bd))

	req := factoryRequest(*base).withHeaders(headers).build()


	b, _ := (*client).Do(req)

	dest := make(map[string]interface{})

	err := json.Unmarshal(b, &dest)
	if err != nil {
		return "", err
	}

	return dest["uri"].(string), nil

}

//given the difference between what we have the target structure saved locally and what we want (the current state on the Spotify API)
//Apply the requisite changes to patch the drainlist
func patchDrainlist(accessToken string, client *clientFacade, target *Drainlist) error {
	toAdd, toRem := computeDelta(accessToken, client, target)

	sort.Strings(toAdd)
	sort.Strings(toRem)

	_, _, toRem = comm(toAdd, toRem) //you discard add - rem and change rem to equal rem - add, this prevents you from removing songs that another list has added

	current := getTracks(accessToken, client, "", target.backing)

	_, toRem, _ = comm(current, toRem) //want to remove all items that are in remove and in current
	_, _ , toAdd = comm(current, toAdd) //want to add all items that are in add and not in current

	_ = removeTracks(accessToken, client, toRem, target.backing)
	_ = addTracks(accessToken, client, toAdd, target.backing)

	target.backing.ref = append(target.backing.ref, toAdd...) //add adds
	sort.Strings(target.backing.ref) //sort
	removeIfBoth(toRem, target.backing.ref) //if in both remove from target.backing.ref (this is effectively for all in toRem: if in target.backing then remove

	//1. (if item in adds and rems, remove from rems)
	//2. DL contents of playlist
	//3. if Item not in playlist and in rems, remove from rems
	//4. if Item in playlist and in adds, remove from adds
	//5. todo update drainlist ref table

	return nil
}

// Compute the items required to be added (and / or removed) between the in memory version of target, and the Spotify version
func computeDelta(accessToken string, client *clientFacade,  target *Drainlist) ([]string, []string) {
	globalAdd := make([]string, 0)
	globalRem := make([]string, 0)
	for i := range target.sources {
		current := getTracks(accessToken, client, "", target.sources[i])
		ref := target.sources[i].ref
		sort.Strings(current)
		sort.Strings(ref)
		toAdd, _ , toRem := comm(current, ref)
		target.sources[i].ref = current //update reference to account for change
		globalAdd = append(globalAdd, toAdd...)
		globalRem = append(globalAdd, toRem...)
	}
	globalAdd = unique(globalAdd)
	globalRem = unique(globalRem)

	return globalAdd,globalRem
}


/*
1. ref list for each source. If different than ref list then send an add or delete to the user list and update ref.
	Would only override user prefs if a song (that user removed) was removed and re-added (Acceptable bug)
	Issue: what if one playlist deletes and another adds?
		Either list priority or default to add and the user can remove (again once a track is removed it is only re-added once a source adds it back)
 */

//get User ID from the tokens
func getUserID(accessToken string, client *clientFacade) (string, error) {
	spoturl := "https://api.spotify.com/v1/me"

	headers := map[string]string{"Authorization":"Bearer " + accessToken, "Content-Type":"application/json"}

	req := createRequest().withURL(spoturl).withHeaders(headers).withMethod("GET").build()
	b, _ := (*client).Do(req)

	dest := make(map[string]interface{})

	err := json.Unmarshal(b, &dest)
	if err != nil {
		return "", err
	}
	return dest["id"].(string), nil
}



package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
	"sort"
	"strings"
)

type Playlist struct {
	user string
	name string
	uri string
	tracks []string
	ref []string
}

type Drainlist struct {
	backing	*Playlist
	sources []*Playlist
}

func getPlaylists(access_token string, client clientFacade, urlOffset string) []Playlist {
	spotUrl := "https://api.spotify.com/v1/me/playlists"
	if urlOffset != "" {
		spotUrl = urlOffset
	}

	headers := map[string]string{"Authorization":"Bearer " + access_token}

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
			retList = append(retList, getPlaylists(access_token, client, next)...)
		}
	}
	return retList
}

func getTracks(access_token string, client *clientFacade, urlOffset string, playlist *Playlist) []string{

	playlist_id := uri2id(playlist.uri)
	_ = make([]string,0)
	spoturl :=  "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
	if urlOffset != "" {
		spoturl = urlOffset
	}

	headers :=  map[string]string {"Authorization": "Bearer " + access_token}

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
			uris = append(uris, getTracks(access_token, client, next, playlist)...)
		}
	}
	return uris

}

func addTracks(access_token string, client *clientFacade, track_uris []string, playlist *Playlist) error {
	spoturl := "https://api.spotify.com/v1/playlists/" + uri2id(playlist.uri) + "/tracks"

	headers := map[string]string{"Authorization":"Bearer " + access_token}

	body := map[string][]string{
		"uris" : track_uris,
	}

	req := createRequest().withURL(spoturl).withHeaders(headers).withBodyJson(body).withMethod("POST").build()


	b, _ := (*client).Do(req)

	resp := string(b)

	if !strings.Contains(resp, "snapshot") {
		return errors.New("error incorrect response\n" + resp)
	}
	return nil
}

func removeTracks(access_token string, client *clientFacade, track_uris []string, playlist *Playlist) error {
	spoturl := "https://api.spotify.com/v1/playlists/" + uri2id(playlist.uri) + "/tracks"

	headers := map[string]string{"Authorization":"Bearer " + access_token, "Content-Type":"application/json"}
	bodyMap := make([]map[string]string, 0)

	for i := range track_uris {
		tMap := make(map[string]string)
		tMap["uri"] = track_uris[i]
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

func createPlaylist(access_token string, client *clientFacade, name string) (string, error) {

	user_id, _ := getUserID(access_token, client)
	spoturl := "https://api.spotify.com/v1/users/" +  user_id + "/playlists"

	headers := map[string]string{"Authorization":"Bearer " + access_token, "Content-Type":"application/json"}
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

func patchDrainlist(access_token string, client *clientFacade, target *Drainlist) error {
	toAdd, toRem := computeDelta(access_token, client, target)

	sort.Strings(toAdd)
	sort.Strings(toRem)

	_, _, toRem = comm(toAdd, toRem) //you discard add - rem and change rem to equal rem - add, this prevents you from removing songs that another list has added

	current := getTracks(access_token, client, "", target.backing)

	_, toRem, _ = comm(current, toRem) //want to remove all items that are in remove and in current
	_, _ , toAdd = comm(current, toAdd) //want to add all items that are in add and not in current

	_ = removeTracks(access_token, client, toRem, target.backing)
	_ = addTracks(access_token, client, toAdd, target.backing)

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


func computeDelta(access_token string, client *clientFacade,  target *Drainlist) ([]string, []string) {
	globalAdd := make([]string, 0)
	globalRem := make([]string, 0)
	for i := range target.sources {
		current := getTracks(access_token, client, "", target.sources[i])
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


func getUserID(access_token string, client *clientFacade) (string, error) {
	spoturl := "https://api.spotify.com/v1/me"

	headers := map[string]string{"Authorization":"Bearer " + access_token, "Content-Type":"application/json"}

	req := createRequest().withURL(spoturl).withHeaders(headers).withMethod("GET").build()
	b, _ := (*client).Do(req)

	dest := make(map[string]interface{})

	err := json.Unmarshal(b, &dest)
	if err != nil {
		return "", err
	}
	return dest["id"].(string), nil
}



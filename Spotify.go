package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

var client_id, client_secret = getSecrets()

var myUrl = "http://127.0.0.1:5000/"
var user = "Danny"
var cwd = "/Users/Danny/Documents/CS/GoSpotifyAppend"
var uri_header = "spotify:playlist:"

func init_handler()(h http.Handler){
	return http.RedirectHandler(get_new_tokens(), 302)
}

func hello(w http.ResponseWriter, r *http.Request) {

	code := parseCode(r.URL.String())
	_, _ = w.Write([]byte("code is " + code))
	tokens := get_tokens_from_code(code, spotifyClient{})
	save_tokens(tokens, user, time.Now().Unix())
}


func main() {
	//http.Handle("/",init_handler())
	//http.HandleFunc("/authentication_return", hello)
	//_ = http.ListenAndServe(":5000", nil)
	client := spotifyClient(http.Client{})
	a := getPlaylists(get_access_token(user, time.Now().Unix(), client), client, "")
	fmt.Println(a)

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
	fmt.Println(string(b))

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

			tracks:nil, //todo get a function to fetch these
			reference:false,
		}
		retList = append(retList, list)
		//todo also deal with the whole 20 list max return deal
	}
	var next string
	if dest["next"] != nil { //check next is not null
		next = dest["next"].(string) //cast to string since something is there
		if next != "" { //recurse
			retList = append(retList, getPlaylists(access_token, client, next)...)
		}
	}
	return retList //todo does this even work (yes)
}

func getTracks(access_token string, client clientFacade, urlOffset string, playlist Playlist) {

	   playlist_id := uri2id(playlist.uri)
	   _ = make([]string,0)
	   spoturl :=  "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"

	   headers :=  map[string]string {"Authorization": "Bearer " + access_token}

	   req := createRequest().withURL(spoturl).withHeaders(headers).withMethod("GET").build()

	   b, _ := client.Do(req)
	   fmt.Println(string(b))
	   //works
	   //next is nil if not a URI
	   //items contains the tracks, gamer gamer
}

func uri2id(uri string) string {
	return strings.Split(uri, ":")[2]
}


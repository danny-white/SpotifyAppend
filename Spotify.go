package main

import (
	"net/http"
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
	http.Handle("/",init_handler())
	http.HandleFunc("/authentication_return", hello)
	_ = http.ListenAndServe(":5000", nil)

}

func getPlaylists(access_token string, client clientFacade) {
	url := "https://api.spotify.com/v1/me/playlists"
	headers := make(map[string]string)
	headers["Authorization"] = "Bearer " + access_token
	_ = url

	req, _ := http.NewRequest("GET", url, nil)

	for k,v := range headers {
		req.Header.Add(k,v)
	}
	_, _ = client.Do(req)
}


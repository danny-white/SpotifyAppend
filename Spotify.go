package main

import (
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
	tokens := get_tokens_from_code(code, &spotifyClient{})
	save_tokens(tokens, user, time.Now().Unix())
}


func main() {
	http.Handle("/",init_handler())
	http.HandleFunc("/authentication_return", hello)
	_ = http.ListenAndServe(":5000", nil)
	//get_new_tokens()
}


func uri2id(uri string) string {
	return strings.Split(uri, ":")[2]
}


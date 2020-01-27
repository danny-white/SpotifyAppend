package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
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
	tokens := get_tokens_from_code(code)
	save_tokens(tokens)
}

func save_tokens(tokens tokenResponse) {
	serialTokens := convertToken(tokens)
	file, _ := json.Marshal(serialTokens)
	_ = ioutil.WriteFile(user + "/" + user + "_tokens", file, 0644)
}

func load_tokens(user string) tokenSerialized {
	input, _ := ioutil.ReadFile(user + "/" + user + "_tokens")
	serialTokens := tokenSerialized{}
	_ = json.Unmarshal(input, serialTokens)
	return serialTokens
}

func parseCode(url string) string {
	return strings.Split(strings.Split(url, "?")[1], "=")[1]
}


func main() {
	http.Handle("/",init_handler())
	http.HandleFunc("/authentication_return", hello)
	_ = http.ListenAndServe(":5000", nil)

}


func getSecrets() (string, string){
	dat, err :=ioutil.ReadFile("Secrets")
	if err != nil {
		fmt.Print("shit's broke ")
		fmt.Print(err)
	}
	secrets := strings.Split(string(dat), "\n")
	return secrets[0], secrets[1]

}

func getPlaylists(access_token string) {
	url := "https://api.spotify.com/v1/me/playlists"
	headers := make(map[string]string)
	headers["Authorization"] = "Bearer " + access_token
	_ = url

	client := &http.Client{}

	req, _ := http.NewRequest("GET", url, nil)

	for k,v := range headers {
		req.Header.Add(k,v)
	}
	_, _ = client.Do(req)
}
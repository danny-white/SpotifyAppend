package main

import (
	"encoding/json"
	"net/http"
	"time"
)

var clientId, clientSecret = getSecrets()

var myUrl = "http://127.0.0.1:5000/"
var user = "Danny"

var client clientFacade = &spotifyClient{}

func handleInit()(h http.Handler){
	//return a session cookie
	return http.RedirectHandler(getNewTokens(), 302)
}

func handleInitLanding(w http.ResponseWriter, r *http.Request) {
	code := parseCode(r.URL.String())
	_, _ = w.Write([]byte("code is " + code))
	tokens := getTokensFromCode(code, &spotifyClient{})
	saveTokens(tokens, user, time.Now().Unix())
	//at this point we should redirect back to the frontend
}

func handleGetPlaylists(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	var token = loadTokens(user)
	var plists = getPlaylists(user, token.Access_token, client, "")
	var retval = make([]string, len(plists))
	for i  := range plists {
		retval[i] =  plists[i].name
	}
	enc := json.NewEncoder(w)
	_ = enc.Encode(retval)
}

func handleCreateDrain(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	var token = loadTokens(user)

	//get request with json body which will contain a list of drains to sync

	//crete drain, first empty from name, then allow create + add sources
	var playlist, err = createPlaylist(token.Access_token, &client, "gamerTestNewList")
	if err != nil  {
		panic(err)
	}

	//in addition to creating the drain we need to save something locally so we know we have a drainlist
	//curretnly it's just a blank drainlist, so w/e
	var i = Drainlist{
		backing:&playlist,
		sources:nil,
	}
	err = write(i)
	if err != nil  {
		panic(err)
	}

	_, _ = w.Write([]byte(playlist.uri))
}

//API entry to force sync one or many Drainlists
//todo IP
func handleForceSync(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	var token = loadTokens(user)

	//get request with json body which will contain a list of drains to sync

	var drainlists = parseRequest(r) //parseDrains from request (by name, load from disk)

	for i := range drainlists {
		var drainlist = read(user, drainlists[i])
		var err = patchDrainlist(token.Access_token, &client, &drainlist)
		if err != nil {
			panic(err)
		}
	}

	_, _ = w.Write([]byte("success"))
}

////todo ip
//this is for editing existing,
//func handleEditDrains(w http.ResponseWriter, r *http.Request) {
//	enableCors(&w)
//	var token = loadTokens(user)
//
//	var drainlists []Drainlist //parseDrains from request (by name, load from disk)
//
//	for i := range drainlists {
//
//		if err != nil {
//			panic(err)
//		}
//	}
//	_, _ = w.Write([]byte("success"))
//}

func main() {
	http.Handle("/", handleInit())
	http.HandleFunc("/authentication_return", handleInitLanding)
	http.HandleFunc("/get_playlists", handleGetPlaylists)
	http.HandleFunc("/new_drain", handleCreateDrain)
	_ = http.ListenAndServe(":5000", nil)
}

//todo restrict
func enableCors(w *http.ResponseWriter) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
}

func parseRequest(r *http.Request) []string {

	var drainlists =  make([]string, 0, 0)
	err := json.NewDecoder(r.Body).Decode(drainlists)
	if err != nil {
		panic(err)
	}
	return drainlists
}


package main

import (
	"net/http"
	"time"
)

var clientId, clientSecret = getSecrets()

var myUrl = "http://127.0.0.1:5000/"
var user = "Danny"

func initHandler()(h http.Handler){
	return http.RedirectHandler(getNewTokens(), 302)
}

func hello(w http.ResponseWriter, r *http.Request) {

	code := parseCode(r.URL.String())
	_, _ = w.Write([]byte("code is " + code))
	tokens := getTokensFromCode(code, &spotifyClient{})
	saveTokens(tokens, user, time.Now().Unix())
}

//Here beyond registering the initHandler, which will run the login / sign up portion of the workflow
//Login -> Session Cookie
//we need endpoints for the following:
//get all Plists (user)
	//get()
//Edit Drains (delete drain, add / remove sources)
	//Delete(name)
	//update(name, newState)
//force sync override
	//sync()

func main() {
	http.Handle("/", initHandler())
	http.HandleFunc("/authentication_return", hello)
	_ = http.ListenAndServe(":5000", nil)
	//get_new_tokens()
}


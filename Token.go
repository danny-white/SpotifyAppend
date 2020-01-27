package main

import (
	"encoding/base64"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"time"
)
type tokenResponse struct {
	Access_token string
	Tokentype string
	Expires_in int
	Refresh_token string
	Scope string
}

type tokenSerialized struct {
	Access_token string
	Expires_at int64
	Refresh_token string
}

func convertToken(response tokenResponse) tokenSerialized {
	retTok := tokenSerialized{response.Access_token,0,response.Refresh_token}
	now := time.Now()
	secs := now.Unix()
	retTok.Expires_at = int64(response.Expires_in) + secs
	return retTok
}

func get_tokens_from_code(code string) tokenResponse{
	spoturl := "https://accounts.spotify.com"
	resource := "/api/token/"
	query := map[string]string{
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": myUrl + "authentication_return",
	}

	baseUrl, _ := url.ParseRequestURI(spoturl)
	baseUrl.Path = resource

	params := url.Values{}
	for k , v := range query {
		params.Add(k,v)
	}

	headers := make_authorization_headers(client_id, client_secret)
	req, _ := http.NewRequest("POST", baseUrl.String(), strings.NewReader(params.Encode()))
	for k,v := range headers {
		req.Header.Set(k,v)
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	container := tokenResponse{}

	client := &http.Client{}
	resp, _ := client.Do(req)
	body, _ := ioutil.ReadAll(resp.Body)

	err := json.Unmarshal(body, &container)
	if err != nil {
		panic(err)
	}
	return container
}
func get_new_tokens() string{
	spoturl := "https://accounts.spotify.com/authorize/"
	scopes := "playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative user-follow-read"
	query := map[string]string{
		"client_id" : client_id,
		"response_type" : "code",
		"scope" : scopes,
		"redirect_uri" : myUrl + "authentication_return",
	}
	baseUrl, _ := url.Parse(spoturl)
	params := url.Values{}
	for k , v := range query {
		params.Add(k,v)
	}
	baseUrl.RawQuery = params.Encode()

	return baseUrl.String()
}

func write_new_tokens(user string, tokenJson map[string]string){
}
func get_access_token(user string){
}
func get_refresh_token(user string){
}
func refresh_tokens(user string){
}
func tokenfile_open(user string){
}
func make_authorization_headers(client_id string, client_secret string) map[string]string{
	sEnc := base64.StdEncoding.EncodeToString([]byte(client_id + ":" + client_secret))

	return map[string]string{"Authorization": "Basic " + sEnc}
}
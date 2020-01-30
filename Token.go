package main

import (
	"encoding/json"
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

var spoturl = "https://accounts.spotify.com"

func get_tokens_from_code(code string, client clientFacade ) tokenResponse{
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

	body, err := client.Do(req)
	if err != nil {
		panic(err)
	}

	err = json.Unmarshal(body, &container)
	if err != nil {
		panic(err)
	}
	return container
}

func get_new_tokens() string {
	resource := "/authorize/"
	scopes := "playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative user-follow-read"
	query := map[string]string{
		"client_id" : client_id,
		"response_type" : "code",
		"scope" : scopes,
		"redirect_uri" : myUrl + "authentication_return",
	}

	baseUrl, _ := url.Parse(spoturl)
	baseUrl.Path = resource

	params := url.Values{}
	for k , v := range query {
		params.Add(k,v)
	}
	baseUrl.RawQuery = params.Encode()

	return baseUrl.String()
}


func refresh_tokens(user string, client clientFacade ){
	resource := "/api/token/"
	refreshToken := get_refresh_token(user)
	query := map[string]string{
		"grant_type" : "refresh_token",
		"refresh_token" : refreshToken,
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

	body, err := client.Do(req)
	if err != nil {
		panic(err)
	}

	err = json.Unmarshal(body, &container)
	if err != nil {
		panic(err)
	}

	container.Refresh_token = refreshToken
	save_tokens(container, user, time.Now().Unix())
}
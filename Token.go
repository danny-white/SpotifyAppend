package main

import (
	"encoding/json"
	"net/url"
	"reflect"
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

func get_tokens_from_code(code string, client clientFacade ) tokenResponse{
	resource := "/api/token/"
	params := map[string]string{
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": myUrl + "authentication_return",
	}

	headers := make_authorization_headers(client_id, client_secret)
	headers["Content-Type"] = "application/x-www-form-urlencoded"

	req := createRequest().withURL(SPOTIFY_URL + resource).withMethod("POST").withBody(params).withHeaders(headers).build()

	body, err := client.Do(req)
	if err != nil {
		panic(err)
	}

	container := tokenResponse{}
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

	baseUrl, _ := url.Parse(SPOTIFY_URL)
	baseUrl.Path = resource

	params := url.Values{}
	for k , v := range query {
		params.Add(k,v)
	}
	baseUrl.RawQuery = params.Encode()

	return baseUrl.String()
}


func refresh_tokens(user string, client clientFacade, refreshToken string ){
	resource := "/api/token/"
	params := map[string]string{
		"grant_type" : "refresh_token",
		"refresh_token" : refreshToken,
	}

	headers := make_authorization_headers(client_id, client_secret)
	headers["Content-Type"] = "application/x-www-form-urlencoded"

	req := createRequest().withURL(SPOTIFY_URL + resource).withHeaders(headers).withMethod("POST").withBody(params).build()

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
	if reflect.TypeOf(client).Name() == "mockClient" {
		//only overwrite if we're not doing a test lmao
	} else {
		save_tokens(container, user, time.Now().Unix())
	}

}
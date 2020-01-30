package main

import (
	"io/ioutil"
	"net/http"
	"net/url"
	"reflect"
	"strings"
	"testing"
)
	
func Test_refresh_tokens(t *testing.T) {
	expectedRequest := http.Request{}
	expectedRequest.Header = http.Header{}
	headers := make_authorization_headers(client_id, client_secret)
	for k,v := range headers {
		expectedRequest.Header.Set(k,v)
	}
	expectedRequest.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	expectedRequest.URL, _ = url.ParseRequestURI( "https://accounts.spotify.com/api/token/")

	expectedRequest.Method = "POST"

	params := url.Values{}
	query := map[string]string{
		"grant_type" : "refresh_token",
		"refresh_token" : "testTok",
	}
	for k , v := range query {
		params.Add(k,v)
	}
	readerbody := strings.NewReader(params.Encode())
	expectedBody, _ := ioutil.ReadAll(readerbody)

	type args struct {
		user   string
		client clientFacade
	}
	tests := []struct {
		name string
		args args
	}{
		{
			name:"gamer",
			args: args{
				user:"Danny",
				client:mockClient{
					resp:[]byte(tokRespSer),
					expectedRequest:expectedRequest,
					expectedBody:string(expectedBody),
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			refresh_tokens(tt.args.user, tt.args.client, "testTok")
		})
	}
}

func Test_get_new_tokens(t *testing.T) {
	tests := []struct {
		name string
		want string
	}{
		{
			name:"test",
			want:"https://accounts.spotify.com/authorize/?client_id=7a1454711b0e4883affd973ca35a67e2&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fauthentication_return&response_type=code&scope=playlist-read-private+playlist-modify-public+playlist-modify-private+playlist-read-collaborative+user-follow-read",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := get_new_tokens(); got != tt.want {
				t.Errorf("get_new_tokens() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_get_tokens_from_code(t *testing.T) {
	expectedRequest := http.Request{}
	expectedRequest.Header = http.Header{}
	headers := make_authorization_headers(client_id, client_secret)
	for k,v := range headers {
		expectedRequest.Header.Set(k,v)
	}
	expectedRequest.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	expectedRequest.URL, _ = url.ParseRequestURI( "https://accounts.spotify.com/api/token/")

	expectedRequest.Method = "POST"

	params := url.Values{}
	query := map[string]string{
		"grant_type": "authorization_code",
		"code": "gamerCodeTime",
		"redirect_uri": myUrl + "authentication_return",
	}
	for k , v := range query {
		params.Add(k,v)
	}
	readerbody := strings.NewReader(params.Encode())
	expectedBody, _ := ioutil.ReadAll(readerbody)

	type args struct {
		code   string
		client clientFacade
	}
	tests := []struct {
		name string
		args args
		want tokenResponse
	}{
		{
			name: "name",
			args: args{
				code:"gamerCodeTime",
				client: mockClient{
					resp:[]byte(tokRespSer),
					expectedRequest:expectedRequest,
					expectedBody:string(expectedBody),
				},
			},
			want:tokResp,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := get_tokens_from_code(tt.args.code, tt.args.client); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("get_tokens_from_code() = %v, want %v", got, tt.want)
			}
		})
	}
}

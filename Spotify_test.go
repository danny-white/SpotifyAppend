package main

import (
	"net/http"
	"reflect"
	"testing"
	"time"
)

func Test_getPlaylists(t *testing.T) {
	clnt := spotifyClient(http.Client{})
	type args struct {
		access_token string
		client       clientFacade
		urlOffset    string
	}
	tests := []struct {
		name string
		args args
		want []Playlist
	}{
		{
			name: "name",
			args: args{
				access_token: get_access_token("Danny", time.Now().Unix(), clnt),
				client:       clnt,
				urlOffset:    "",
			},
			want: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := getPlaylists(tt.args.access_token, tt.args.client, tt.args.urlOffset); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("getPlaylists() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_getTracks(t *testing.T) {
	client := spotifyClient(http.Client{})
	type args struct {
		access_token string
		client       clientFacade
		urlOffset    string
		playlist     Playlist
	}
	tests := []struct {
		name string
		args args
	}{
		{
			name:"test",
			args:args{
				access_token:get_access_token("Danny", time.Now().Unix(), client),
				client:client,
				urlOffset:"",
				playlist:Playlist{
					uri:"spotify:playlist:3S7Hbx2nGmiqf4TLH93QU6",
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			getTracks(tt.args.access_token, tt.args.client, tt.args.urlOffset, tt.args.playlist)
		})
	}
}

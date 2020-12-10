package main

import (
	"net/http"
	"testing"
	"time"
)

//Mock client and test getting a track from playlists
func Test_getTracks(t *testing.T) {
	//todo this fails on empty playlists
	client := spotifyClient(http.Client{})
	clnt := &client
	type args struct {
		accessToken string
		client      clientFacade
		urlOffset   string
		playlist    *Playlist
	}
	tests := []struct {
		name string
		args args
	}{
		{
			name:"test",
			args:args{
				accessToken: getAccess_token("Danny", time.Now().Unix(), clnt),
				client:      clnt,
				urlOffset:   "",
				playlist: &Playlist{
					uri:"spotify:playlist:3S7Hbx2nGmiqf4TLH93QU6",
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			getTracks(tt.args.accessToken, &tt.args.client, tt.args.urlOffset, tt.args.playlist)
		})
	}
}

func Test_addTracks(t *testing.T) {
	client := spotifyClient(http.Client{})
	clnt := &client
	type args struct {
		accessToken string
		client      clientFacade
		trackUris   []string
		playlist    *Playlist
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		{
			name: "test",
			args:args{
				accessToken: getAccess_token("Danny", time.Now().Unix(), clnt),
				client:      clnt,
				trackUris:   []string{"spotify:track:3Gi9XELDEagGny8QInTscT"},
				playlist: &Playlist{
					uri:"spotify:playlist:3piBeXM92B6Mfw3PGbzKCk",
				},
			},
			wantErr:false,
		},

	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := addTracks(tt.args.accessToken, &tt.args.client, tt.args.trackUris, tt.args.playlist); (err != nil) != tt.wantErr {
				t.Errorf("addTracks() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func Test_removeTracks(t *testing.T) {
	client := spotifyClient(http.Client{})
	clnt := &client
	type args struct {
		accessToken string
		client      clientFacade
		trackUris   []string
		playlist    *Playlist
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		{
			name:"test",
			args:args{
				accessToken: getAccess_token("Danny", time.Now().Unix(), clnt),
				client:      clnt,
				trackUris:   []string{"spotify:track:3Gi9XELDEagGny8QInTscT"},
				playlist: &Playlist{
					uri:"spotify:playlist:3piBeXM92B6Mfw3PGbzKCk",
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := removeTracks(tt.args.accessToken, &tt.args.client, tt.args.trackUris, tt.args.playlist); (err != nil) != tt.wantErr {
				t.Errorf("removeTracks() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func Test_getUserID(t *testing.T) {
	client := spotifyClient(http.Client{})
	clnt := &client
	type args struct {
		accessToken string
		client      clientFacade
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name:"test",
			args:args{
				accessToken: getAccess_token("Danny", time.Now().Unix(), clnt),
				client:      clnt,
			},
			want:"rdqv6wucfa41oo0yhkbv1k8ar",
			wantErr:false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := getUserID(tt.args.accessToken, &tt.args.client)
			if (err != nil) != tt.wantErr {
				t.Errorf("getUserID() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("getUserID() got = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_createPlaylist(t *testing.T) {
	client := spotifyClient(http.Client{})
	clnt := &client
	type args struct {
		accessToken string
		client      clientFacade
		name        string
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		{
			name:"test",
			args:args{
				accessToken: getAccess_token("Danny", time.Now().Unix(), clnt),
				client:      clnt,
				name:        "testPlist",
			},

			wantErr:false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if plist, err := createPlaylist(tt.args.accessToken, &tt.args.client, tt.args.name); (err != nil) != tt.wantErr {
				if plist.uri == "" {
					t.Errorf("createPlaylist() error = %v, wantErr %v", err, tt.wantErr)
				}
			}
		})
	}
}

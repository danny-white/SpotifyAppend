package main

import (
	"net/http"
	"reflect"
	"testing"
	"time"
)

var playlistRet = "{\"href\":\"https://api.spotify.com/v1/users/124995713/playlists?offset=0&limit=1\",\"items\":[{\"collaborative\":false,\"description\":\"\",\"external_urls\":{\"spotify\":\"https://open.spotify.com/playlist/3S7Hbx2nGmiqf4TLH93QU6\"},\"href\":\"https://api.spotify.com/v1/playlists/3S7Hbx2nGmiqf4TLH93QU6\",\"id\":\"3S7Hbx2nGmiqf4TLH93QU6\",\"images\":[{\"height\":640,\"url\":\"https://mosaic.scdn.co/640/21a8c6a6cfaf954f970e068acf4b3a369fdcf6d7ab67616d0000b2731fd509ee61d728a2d3eef921df46b06b4fe41e2e4eb32593e191521b392dd1fff43680a965dddd2379a3de3c535d8d416f3d8e61\",\"width\":640},{\"height\":300,\"url\":\"https://mosaic.scdn.co/300/21a8c6a6cfaf954f970e068acf4b3a369fdcf6d7ab67616d0000b2731fd509ee61d728a2d3eef921df46b06b4fe41e2e4eb32593e191521b392dd1fff43680a965dddd2379a3de3c535d8d416f3d8e61\",\"width\":300},{\"height\":60,\"url\":\"https://mosaic.scdn.co/60/21a8c6a6cfaf954f970e068acf4b3a369fdcf6d7ab67616d0000b2731fd509ee61d728a2d3eef921df46b06b4fe41e2e4eb32593e191521b392dd1fff43680a965dddd2379a3de3c535d8d416f3d8e61\",\"width\":60}],\"name\":\"N\",\"owner\":{\"display_name\":\"Danny White\",\"external_urls\":{\"spotify\":\"https://open.spotify.com/user/124995713\"},\"href\":\"https://api.spotify.com/v1/users/124995713\",\"id\":\"124995713\",\"type\":\"user\",\"uri\":\"spotify:user:124995713\"},\"primary_color\":null,\"public\":true,\"snapshot_id\":\"NCwxNjQ2MzRkMmFmNjExMzExZThlNThmMzdiNWI5Y2UwZGU1ZmFlYmEw\",\"tracks\":{\"href\":\"https://api.spotify.com/v1/playlists/3S7Hbx2nGmiqf4TLH93QU6/tracks\",\"total\":33},\"type\":\"playlist\",\"uri\":\"spotify:playlist:3S7Hbx2nGmiqf4TLH93QU6\"}],\"limit\":1,\"next\":\"\",\"offset\":0,\"previous\":null,\"total\":33}"

var trackRet = "{\"href\":\"https://api.spotify.com/v1/playlists/3S7Hbx2nGmiqf4TLH93QU6/tracks?offset=0&limit=1\",\"items\":[{\"added_at\":\"2019-12-12T02:16:22Z\",\"added_by\":{\"external_urls\":{\"spotify\":\"https://open.spotify.com/user/124995713\"},\"href\":\"https://api.spotify.com/v1/users/124995713\",\"id\":\"124995713\",\"type\":\"user\",\"uri\":\"spotify:user:124995713\"},\"is_local\":false,\"primary_color\":null,\"track\":{\"album\":{\"album_type\":\"album\",\"artists\":[{\"external_urls\":{\"spotify\":\"https://open.spotify.com/artist/2CIMQHirSU0MQqyYHq0eOx\"},\"href\":\"https://api.spotify.com/v1/artists/2CIMQHirSU0MQqyYHq0eOx\",\"id\":\"2CIMQHirSU0MQqyYHq0eOx\",\"name\":\"deadmau5\",\"type\":\"artist\",\"uri\":\"spotify:artist:2CIMQHirSU0MQqyYHq0eOx\"}],\"available_markets\":[],\"external_urls\":{\"spotify\":\"https://open.spotify.com/album/28KIq6kRfU2cASg8VEAhLF\"},\"href\":\"https://api.spotify.com/v1/albums/28KIq6kRfU2cASg8VEAhLF\",\"id\":\"28KIq6kRfU2cASg8VEAhLF\",\"images\":[{\"height\":640,\"url\":\"https://i.scdn.co/image/ab67616d0000b273eece170d64581ecebf20d3a0\",\"width\":640},{\"height\":300,\"url\":\"https://i.scdn.co/image/ab67616d00001e02eece170d64581ecebf20d3a0\",\"width\":300},{\"height\":64,\"url\":\"https://i.scdn.co/image/ab67616d00004851eece170d64581ecebf20d3a0\",\"width\":64}],\"name\":\"Random Album Title\",\"release_date\":\"2008\",\"release_date_precision\":\"year\",\"total_tracks\":12,\"type\":\"album\",\"uri\":\"spotify:album:28KIq6kRfU2cASg8VEAhLF\"},\"artists\":[{\"external_urls\":{\"spotify\":\"https://open.spotify.com/artist/2CIMQHirSU0MQqyYHq0eOx\"},\"href\":\"https://api.spotify.com/v1/artists/2CIMQHirSU0MQqyYHq0eOx\",\"id\":\"2CIMQHirSU0MQqyYHq0eOx\",\"name\":\"deadmau5\",\"type\":\"artist\",\"uri\":\"spotify:artist:2CIMQHirSU0MQqyYHq0eOx\"}],\"available_markets\":[],\"disc_number\":1,\"duration_ms\":450000,\"episode\":false,\"explicit\":false,\"external_ids\":{\"isrc\":\"GBTDG0800013\"},\"external_urls\":{\"spotify\":\"https://open.spotify.com/track/3Gi9XELDEagGny8QInTscT\"},\"href\":\"https://api.spotify.com/v1/tracks/3Gi9XELDEagGny8QInTscT\",\"id\":\"3Gi9XELDEagGny8QInTscT\",\"is_local\":false,\"name\":\"Alone With You\",\"popularity\":0,\"preview_url\":null,\"track\":true,\"track_number\":6,\"type\":\"track\",\"uri\":\"spotify:track:3Gi9XELDEagGny8QInTscT\"},\"video_thumbnail\":{\"url\":null}}],\"limit\":1,\"next\":\"\",\"offset\":0,\"previous\":null,\"total\":33}"

func Test_getPlaylists(t *testing.T) {
	clnt := mockClient{
		resp:[]byte(playlistRet),
		expectedRequest: nil,
		expectedBody:"",
	}

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
			name: "noNext",
			args: args{
				access_token: get_access_token("Danny", time.Now().Unix(), clnt),
				client:       clnt,
				urlOffset:    "",
			},
			want: []Playlist{
				{
					user: "Danny",
					name:"N",
					uri :"spotify:playlist:3S7Hbx2nGmiqf4TLH93QU6",
					tracks : nil,
					reference :false,
				},
			},
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
	//client := mockClient{
	//	resp:[]byte(trackRet),
	//	expectedRequest: nil,
	//	expectedBody:"",
	//}
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

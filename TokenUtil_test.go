package main

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"reflect"
	"strings"
	"testing"
)

var access = "Atok"
var refresh = "Rtok"
var tokFile = "{\"Access_token\":\"" + access + "\",\"Expires_at\":1234,\"Refresh_token\":\""+ refresh + "\"}"
var TestUser = "Test"

var tokSer = tokenSerialized{access, 1234, refresh}
var tokResp = tokenResponse{access, "A", 1234, refresh, "a"}
var tokRespSer = "{\"Access_token\":\"Atok\",\"Tokentype\":\"A\",\"Expires_in\":1234,\"Refresh_token\":\"Rtok\",\"Scope\":\"a\"}"

func Test_parseCosde(t *testing.T) {
	s, _ := json.Marshal(tokResp)
	if string(s) != "{\"Access_token\":\"Atok\",\"Tokentype\":\"A\",\"Expires_in\":1234,\"Refresh_token\":\"Rtok\",\"Scope\":\"a\"}" {
		t.Error("you blew it gamer")
	}
}

func Test_parseCode(t *testing.T) {
	type args struct {
		url string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "big t1",
			args: args{
				url: "http://127.0.0.1:5000/authentication_return?code=AQBzZPftO11imxSz5l-JkUte8_WyIY8HAsoqPyhZzO8XfW-lPcdvBXP6uffHo1GpDGhJ-c72eKjqRvd4lUFp7SlHEDKrB3KXC3aqWAsBN1CYTOZzXX9iGbn7duzbqD_LLxuGZ4CvM7FMi_Zw-u0_FkZpFLSpuQ9SKCvo2Mdui6a5AnHQB1UdoxpcwoCd8lykPwjvlYs6eKLlxqjLUaPDfi7UvmU-mO9fIZLPR5yBJQBRfcBueYZRqHIhzp-nRx7p1pNl1c1A5PyWkKsKAxh2w_XyoDzQLTB6vdrn0exiMW5G8TLipa801Vt-zXjThpxXMdZ3odaWOYvH5sAJRiF-7QgY0W_JrZOxguqUaWQk1yr8inJ1ozoaTw",
			},
			want: "AQBzZPftO11imxSz5l-JkUte8_WyIY8HAsoqPyhZzO8XfW-lPcdvBXP6uffHo1GpDGhJ-c72eKjqRvd4lUFp7SlHEDKrB3KXC3aqWAsBN1CYTOZzXX9iGbn7duzbqD_LLxuGZ4CvM7FMi_Zw-u0_FkZpFLSpuQ9SKCvo2Mdui6a5AnHQB1UdoxpcwoCd8lykPwjvlYs6eKLlxqjLUaPDfi7UvmU-mO9fIZLPR5yBJQBRfcBueYZRqHIhzp-nRx7p1pNl1c1A5PyWkKsKAxh2w_XyoDzQLTB6vdrn0exiMW5G8TLipa801Vt-zXjThpxXMdZ3odaWOYvH5sAJRiF-7QgY0W_JrZOxguqUaWQk1yr8inJ1ozoaTw",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := parseCode(tt.args.url); got != tt.want {
				t.Errorf("parseCode() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_load_tokens(t *testing.T) {
	createTestTokens()
	type args struct {
		user string
	}
	tests := []struct {
		name string
		args args
		want tokenSerialized
	}{
		{
			name: "gamer test",
			args: args{
				user: TestUser,
			},
			want: tokSer,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := loadTokens(tt.args.user); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("load_tokens() = %v, want %v", got, tt.want)
			}
		})
	}
	removeTestTokens()
}
func createTestTokens() {
	_ = os.Mkdir(TestUser, 0755)
	_ = ioutil.WriteFile(userToPath(TestUser), []byte(tokFile), 0644)
}

func removeTestTokens() {
	_ = os.Remove(userToPath(TestUser))
	_ = os.Remove(TestUser)
}

func Test_save_tokens(t *testing.T) {
	_ = os.Mkdir(TestUser, 0755)
	type args struct {
		tokens tokenResponse
	}
	tests := []struct {
		name string
		args args
	}{
		{
			name: "gamer test",
			args: args{
				tokens: tokResp,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			saveTokens(tt.args.tokens, TestUser, 0)
			saveTeardown(t)
		})
	}
	removeTestTokens()
}

func saveTeardown(t *testing.T) {
	data, _ := ioutil.ReadFile(userToPath(TestUser))
	if strings.Compare(tokFile, string(data)) != 0 {
		t.Fail()
	}
}

func Test_convertToken(t *testing.T) {
	tokSer2 := tokSer
	tokSer2.Expires_at += 100
	type args struct {
		response tokenResponse
		now      int64
	}
	tests := []struct {
		name string
		args args
		want tokenSerialized
	}{
		{
			name: "test",
			args: args{
				response: tokResp,
				now:      0,
			},
			want: tokSer,
		},
		{
			name: "test",
			args: args{
				response: tokResp,
				now:      100,
			},
			want: tokSer2,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := convertToken(tt.args.response, tt.args.now); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("convertToken() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_make_authorization_headers(t *testing.T) {
	type args struct {
		clientId     string
		clientSecret string
	}
	tests := []struct {
		name string
		args args
		want map[string]string
	}{
		{
			name: "name",
			args: args{
				clientId:     "gamer",
				clientSecret: "time",
			},
			want: map[string]string{
				"Authorization": "Basic Z2FtZXI6dGltZQ==",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := makeAuthorizationHeaders(tt.args.clientId, tt.args.clientSecret); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("make_authorization_headers() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_get_Access_token(t *testing.T) {
	createTestTokens()
	type args struct {
		user string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "Does Not Refresh",
			args: args{
				user: TestUser,
			},
			want: access,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := getAccess_token(tt.args.user, 0, &spotifyClient{}); got != tt.want {
				t.Errorf("get_Access_token() = %v, want %v", got, tt.want)
			}
		})
	}
	removeTestTokens()
}

func Test_get_refresh_token(t *testing.T) {
	createTestTokens()
	type args struct {
		user string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name:"test",
			args: args{
				user:TestUser,
			},
			want:refresh,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := getRefreshToken(tt.args.user); got != tt.want {
				t.Errorf("get_refresh_token() = %v, want %v", got, tt.want)
			}
		})
	}
	removeTestTokens()
}

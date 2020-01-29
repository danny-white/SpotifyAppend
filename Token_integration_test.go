package main

import (
	"net/http"
	"testing"
)

var integUser = "Danny"

func Test_refresh_tokens(t *testing.T) {
	token1 := load_tokens(integUser)
	type args struct {
		user string
	}
	tests := []struct {
		name string
		args args
	}{
		{
			name: "test",
			args: args{
				user:integUser,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			refresh_tokens(tt.args.user, &http.Client{})
			verifyRefresh(t, token1)
		})
	}
}
func verifyRefresh(t *testing.T, token1 tokenSerialized) {
	token2 := load_tokens(integUser)

	expBool := token1.Expires_at != token2.Expires_at
	accBool := token1.Access_token != token2.Access_token
	refBool := token1.Refresh_token == token2.Refresh_token
	if !(expBool && accBool && refBool) {
		t.Fail()
	}
}

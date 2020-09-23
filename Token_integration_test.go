package main

import (
	"testing"
)

var integUser = "Danny"

func Test_refresh_tokens_integ(t *testing.T) {
	token1 := loadTokens(integUser)
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
			refreshTokens(tt.args.user, &spotifyClient{}, getRefreshToken(integUser))
			verifyRefresh(t, token1)
		})
	}
}
func verifyRefresh(t *testing.T, token1 tokenSerialized) {
	token2 := loadTokens(integUser)

	expBool := token1.ExpiresAt != token2.ExpiresAt
	accBool := token1.AccessToken != token2.AccessToken
	refBool := token1.RefreshToken == token2.RefreshToken
	if !(expBool && accBool && refBool) {
		t.Fail()
	}
}

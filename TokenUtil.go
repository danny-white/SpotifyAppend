package main

import (
	"encoding/base64"
	"encoding/json"
	"io/ioutil"
	"strings"
)

func convertToken(response tokenResponse, now int64) tokenSerialized {
	retTok := tokenSerialized{response.AccessToken,0,response.RefreshToken}
	retTok.ExpiresAt = int64(response.ExpiresIn) + now
	return retTok
}

func saveTokens(tokens tokenResponse, user string, now int64) {
	serialTokens := convertToken(tokens, now)
	file, _ := json.Marshal(serialTokens)
	err := ioutil.WriteFile(userToPath(user), file, 0644)
	if err != nil {
		panic(err)
	}
}

func loadTokens(user string) tokenSerialized {
	input, _ := ioutil.ReadFile(userToPath(user))
	serialTokens := tokenSerialized{}
	err := json.Unmarshal(input, &serialTokens)
	if err != nil {
		panic(err)
	}
	return serialTokens
}

func parseCode(url string) string {
	return strings.Split(strings.Split(url, "?")[1], "=")[1]
}

func getAccessToken(user string, now int64, client clientFacade) string {
	tokenSer := loadTokens(user)

	// if the token is going to expire in the next minute, refresh
	if tokenSer.ExpiresAt < now+ 60 {
		refreshTokens(user, client, getRefreshToken(user))
	}
	return loadTokens(user).AccessToken
}
func getRefreshToken(user string) string {
	return loadTokens(user).RefreshToken
}

func userToPath(user string) string {
	return user + "/" + user + "_tokens"
}

func makeAuthorizationHeaders(clientId string, clientSecret string) map[string]string{
	sEnc := base64.StdEncoding.EncodeToString([]byte(clientId + ":" + clientSecret))
	return map[string]string{"Authorization": "Basic " + sEnc}
}
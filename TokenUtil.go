package main

import (
	"encoding/base64"
	"encoding/json"
	"io/ioutil"
	"strings"
)

func convertToken(response tokenResponse, now int64) tokenSerialized {
	retTok := tokenSerialized{response.Access_token,0,response.Refresh_token}
	retTok.Expires_at = int64(response.Expires_in) + now
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

//XXX don't change to client*, breaks things
func getAccess_token(user string, now int64, client clientFacade) string {
	tokenSer := loadTokens(user)

	// if the token is going to expire in the next minute, refresh
	if tokenSer.Expires_at < now+ 60 {
		refreshTokens(user, client, getRefreshToken(user))
	}
	return loadTokens(user).Access_token
}
func getRefreshToken(user string) string {
	return loadTokens(user).Refresh_token
}

func userToPath(user string) string {
	return user + "/" + user + "_tokens"
}

func makeAuthorizationHeaders(clientId string, clientSecret string) map[string]string{
	sEnc := base64.StdEncoding.EncodeToString([]byte(clientId + ":" + clientSecret))
	return map[string]string{"Authorization": "Basic " + sEnc}
}
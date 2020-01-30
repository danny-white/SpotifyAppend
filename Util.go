package main

import (
	"io/ioutil"
	"strings"
)

func getSecrets() (string, string){
	dat, err := ioutil.ReadFile("Secrets")
	if err != nil {
		panic(err)
	}
	secrets := strings.Split(string(dat), "\n")
	return secrets[0], secrets[1]
}

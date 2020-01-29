package main

import (
	"fmt"
	"io/ioutil"
	"strings"
)

func getSecrets() (string, string){
	dat, err := ioutil.ReadFile("Secrets")
	if err != nil {
		fmt.Print("shit's broke ")
		fmt.Print(err)
	}
	secrets := strings.Split(string(dat), "\n")
	return secrets[0], secrets[1]
}

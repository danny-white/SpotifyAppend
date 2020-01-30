package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)
// here you effectively extend the method Do, now you can have a faux implementation of http.client and with some DI
// you can get bona-fide unit tests that don't exit the local box, just change client.do to do what you want,
// in this case probably just return some values, but it can literally be anything
// you can't just inline define a solution to the iface, you need a struct looks like
type clientFacade interface {
	Do(req *http.Request)([]byte, error)
}
type mockClient struct {
	resp []byte
	expectedRequest http.Request
}

type spotifyClient http.Client

func (client mockClient) Do(req *http.Request) ([]byte, error){
	resp := client.resp
	return resp, client.validateRequest(req)
}

func (client mockClient) validateRequest(req *http.Request) error {
	if req == nil {
		return nil
	}
	//todo should validate on method, url, header, body (have to tease it out to string from io.closer)
	return fmt.Errorf("arg request did not match expected got: %v, wanted %v", req, client.expectedRequest)
}

func (client spotifyClient) Do(req *http.Request) ([]byte, error) {
	nativeClient := http.Client(client)
	resp, err := nativeClient.Do(req)
	if err != nil {
		return []byte{},err
	}
	body ,err :=ioutil.ReadAll(resp.Body)
	if err != nil {
		return []byte{},err
	}
	err = resp.Body.Close()
	return body, err
}



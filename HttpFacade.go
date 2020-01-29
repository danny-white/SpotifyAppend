package main

import "net/http"
// here you effectively extend the method Do, now you can have a faux implementation of http.client and with some DI
// you can get bona-fide unit tests that don't exit the local box, just change client.do to do what you want,
// in this case probably just return some values, but it can literally be anything
// you can't just inline define a solution to the iface, you need a struct looks like
type clientFacade interface {
	Do(req *http.Request)(*http.Response, error)
}
type mockClient struct {
	resp http.Response
}

type spotifyClient http.Client

func (client mockClient) Do(req *http.Request) (*http.Response, error){
	resp := &client.resp
	return resp, nil
}

func (client spotifyClient) Do(req *http.Request) (*http.Response, error) {
	nativeClient := http.Client(client)
	return nativeClient.Do(req)
}



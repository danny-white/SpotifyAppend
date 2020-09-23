package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"reflect"
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
	expectedRequest *http.Request
	expectedBody string
}

type spotifyClient http.Client

func (client *mockClient) Do(req *http.Request) ([]byte, error){
	resp := client.resp
	return resp, client.validateRequest(req)
}

func (client *mockClient) validateRequest(req *http.Request) error {
	if req == nil || client.expectedRequest == nil {
		return nil
	}
	//validate headers
	eq := true
	//headers
	eq = reflect.DeepEqual(client.expectedRequest.Header, req.Header) && eq
	if !eq {
		fmt.Print("want: ")
		fmt.Println(client.expectedRequest.Header)
		fmt.Print("have: ")
		fmt.Println(req.Header)
	}
	//url
	eq = reflect.DeepEqual(client.expectedRequest.URL, req.URL) && eq
	if !eq {
		fmt.Print("want: ")
		fmt.Println(client.expectedRequest.URL)
		fmt.Print("have: ")
		fmt.Println(req.URL)
	}
	//method
	eq = reflect.DeepEqual(client.expectedRequest.Method, req.Method) && eq
	if !eq {
		fmt.Print("want: ")
		fmt.Println(client.expectedRequest.Method)
		fmt.Print("have: ")
		fmt.Println(req.Method)
	}

	//body

	bodybyte, _ := ioutil.ReadAll(req.Body)
	body := string(bodybyte)
	eq = reflect.DeepEqual(client.expectedBody, body) && eq
	if !eq {
		fmt.Print("want: ")
		fmt.Println(client.expectedBody)
		fmt.Print("have: ")
		fmt.Println(body)
	}

	_ = req.Body.Close()
	if eq {
		return nil
	} else {
		return fmt.Errorf("arg request did not match expected got: %v, wanted %v", req, client.expectedRequest)
	}
}

func (client *spotifyClient) Do(req *http.Request) ([]byte, error) {
	nativeClient := (*http.Client)(client)
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



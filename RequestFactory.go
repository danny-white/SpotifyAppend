package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
)

//Builds http Requests Factory / Builder Style
type factoryRequest http.Request

func (req factoryRequest) withHeaders(headers map[string]string) factoryRequest {
	req.Header = http.Header{}
	for k,v := range headers { //add headers
		req.Header.Add(k,v)
	}
	return req
}

func (req factoryRequest) withBody(body map[string]string) factoryRequest {

	params := url.Values{} //gen body
	for k , v := range body { //add the params
		params.Add(k,v)
	}
	req.Body = ioutil.NopCloser(strings.NewReader(params.Encode()))
	return req
}

func (req factoryRequest) withBodyJson(body map[string][]string) factoryRequest {
	s, _ := json.Marshal(body)
	req.Body = ioutil.NopCloser(strings.NewReader(string(s)))
	return req
}
func (req factoryRequest) withBaseReqeust(base http.Request) factoryRequest {
	return factoryRequest(base)
}

func (req factoryRequest) withQuery(query map[string]string) factoryRequest {
	if req.URL == nil {
		fmt.Println("unable to add query if there is no url present to add to")
		return req
	}

	urlQuery := url.Values{}
	for k , v := range query { //add the params
		urlQuery.Add(k,v)
	}

	req.URL.RawQuery = urlQuery.Encode()
	return req
}

func (req factoryRequest) withMethod(method string) factoryRequest {
	req.Method = method
	return req
}

//takes in the whole url both host and path
func (req factoryRequest) withURL(spoturl string) factoryRequest {
	req.URL, _ = url.ParseRequestURI(spoturl)
	return req
}

func (req factoryRequest) build() *http.Request {
	toRet := http.Request(req)
	return &toRet
}

func createRequest() factoryRequest{
	return factoryRequest(http.Request{})
}



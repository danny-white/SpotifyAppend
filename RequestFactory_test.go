package main

import (
	"io/ioutil"
	"net/url"
	"reflect"
	"strings"
	"testing"
)

func Test_factoryRequest_withHeaders(t *testing.T) {
	type args struct {
		headers map[string]string
	}
	tests := []struct {
		name string
		req  factoryRequest
		args args
		want factoryRequest
	}{
		{
			name:"name",
			req:factoryRequest{},
			args:args{
				headers: map[string]string{
					"a real life" : "header",
				},
			},
			want:factoryRequest{
				Header: map[string][]string{
					"a real life":{"header"}},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := factoryRequest{}
			if got := req.withHeaders(tt.args.headers); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("factoryRequest.withHeaders() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_factoryRequest_withBody(t *testing.T) {
	type args struct {
		body map[string]string
	}
	tests := []struct {
		name string
		req  factoryRequest
		args args
		want factoryRequest
	}{
		{
			name:"name",
			req:factoryRequest{},
			args:args{
				body: map[string]string{
					"a real life" : "body",
				},
			},
			want:factoryRequest{
				Body: ioutil.NopCloser(strings.NewReader("a+real+life=body")),
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := factoryRequest{}
			if got := req.withBody(tt.args.body); !validate(got, tt.want){
				t.Errorf("factoryRequest.withBody() = %v, want %v", got, tt.want)
			}
		})
	}

}
func validate(got factoryRequest, want factoryRequest, ) bool {
	a, _  := ioutil.ReadAll(got.Body)
	b, _  := ioutil.ReadAll(want.Body)
	return reflect.DeepEqual(a,b)
}

func Test_factoryRequest_withQuery(t *testing.T) {
	wantReq := factoryRequest{}
	wantReq.URL, _ = url.Parse("?a+real+life=query")

	type args struct {
		query map[string]string
	}
	tests := []struct {
		name string
		req  factoryRequest
		args args
		want factoryRequest
	}{
		{
			name:"name",
			req:factoryRequest{},
			args:args{
				query: map[string]string{
					"a real life" : "query",
				},
			},
			want:wantReq,
		},

	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := factoryRequest{}
			req.URL, _ = url.Parse("")
			if got := req.withQuery(tt.args.query); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("factoryRequest.withQuery() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_factoryRequest_withMethod(t *testing.T) {
	wantReq := factoryRequest{}
	wantReq.Method = "GET"
	type args struct {
		method string
	}
	tests := []struct {
		name string
		req  factoryRequest
		args args
		want factoryRequest
	}{
		{
			name:"name",
			req:factoryRequest{},
			args:args{
				method:"GET",

			},
			want: wantReq,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := factoryRequest{}
			if got := req.withMethod(tt.args.method); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("factoryRequest.withMethod() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_factoryRequest_withURL(t *testing.T) {
	wantReq := factoryRequest{}
	wantReq.URL, _ = url.ParseRequestURI("gamer.com")
	type args struct {
		spoturl string
	}
	tests := []struct {
		name string
		req  factoryRequest
		args args
		want factoryRequest
	}{
		{
			name:"name",
			req:factoryRequest{},
			args:args{
				spoturl:"gamer.com",

			},
			want: wantReq,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := factoryRequest{}
			if got := req.withURL(tt.args.spoturl); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("factoryRequest.withURL() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_createRequest(t *testing.T) {
	tests := []struct {
		name string
		want factoryRequest
	}{
		{
			name:"name",
			want: factoryRequest{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := createRequest(); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("createRequest() = %v, want %v", got, tt.want)
			}
		})
	}
}

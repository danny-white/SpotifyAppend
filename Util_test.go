package main

import (
	"reflect"
	"testing"
)

func Test_diff(t *testing.T) {
	type args struct {
		a []string
		b []string
	}
	tests := []struct {
		name  string
		args  args
		want  []string
		want1 []string
		want2 []string
	}{
		{

			name: "test",
			args:args{
				a: []string{"1","12","15","2","3","4","6","9"},
				b: []string{"10","12","15", "2","6","7","8","9"},
			},
			want:[]string{"1","3","4"},
			want1:[]string{"12","15","2","6","9"},
			want2:[]string{"10","7","8"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, got1, got2 := comm(tt.args.a, tt.args.b)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("comm() got = %v, want %v", got, tt.want)
			}
			if !reflect.DeepEqual(got1, tt.want1) {
				t.Errorf("comm() got1 = %v, want %v", got1, tt.want1)
			}
			if !reflect.DeepEqual(got2, tt.want2) {
				t.Errorf("comm() got2 = %v, want %v", got2, tt.want2)
			}
		})
	}
}

func Test_removeIfBoth(t *testing.T) {
	type args struct {
		master []string
		slave  []string
	}
	tests := []struct {
		name string
		args args
		want []string
	}{
		{
			name:"test",
			args:args{
				master: []string{"1","12","15","2","3","4","6","9"},
				slave: []string{"10","12","15", "2","6","7","8","9"},
			},
			want: []string{"10","7","8"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := removeIfBoth(tt.args.master, tt.args.slave); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("removeIfBoth() = %v, want %v", got, tt.want)
			}
		})
	}
}
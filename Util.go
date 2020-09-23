package main

import (
	"io/ioutil"
	"sort"
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

/*
	Returns a list of a - b
	set difference
	a and b must be sorted
 */
func comm(a []string, b []string) ([]string, []string , []string){
	if !sort.StringsAreSorted(a) {
		panic("first arr not sorted")
	}
	if !sort.StringsAreSorted(b) {
		panic("second arr not sorted")
	}
	aMinusB := make([]string, 0)
	bMinusA := make([]string, 0)
	comm := make([]string, 0)
	i := 0
	j := 0
	for i < len(a) && j < len(b) {
		if a[i] < b[j] {
			aMinusB = append(aMinusB, a[i])
			i++
		} else if b[j] < a[i] {
			bMinusA = append(bMinusA, b[j])
			j++
		} else {
			comm = append(comm, b[j])
			i++
			j++
		}
	}
	return aMinusB, comm, bMinusA
}

func unique(intSlice []string) []string {
	keys := make(map[string]bool)
	list := []string{}
	for _, entry := range intSlice {
		if _, value := keys[entry]; !value {
			keys[entry] = true
			list = append(list, entry)
		}
	}
	return list
}

func removeIfBoth(master []string, slave []string) []string {
	if !sort.StringsAreSorted(master) {
		panic("first arr not sorted")
	}
	if !sort.StringsAreSorted(slave) {
		panic("second arr not sorted")
	}
	i, j := 0,0
	for i < len(master) && j < len(slave) {
		if master[i] < slave[j] {
			i++
		} else if slave[j] < master[i] {
			j++
		} else {
			copy(slave[j:], slave[j+1:])
			slave = slave[:len(slave)-1]
			i++
		}
	}
	return slave
}
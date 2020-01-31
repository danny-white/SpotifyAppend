package main



type Playlist struct {
	user string
	name string
	uri string
	tracks []string
	reference bool
	// todo add another field to describe a source that tracks additions OR additions and deletions,
	// probably dont need one that only tracks deletions, that'd be weird

}

type Drainlist struct {
	user string
	name string
	uri string //destination uri of the list
	sources []*Playlist
}


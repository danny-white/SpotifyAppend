import json
import os
source_name = "spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb"
ref_name = "spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb"
squaw_name = 'spotify:playlist:5P6Rs7hnXEJtApYHpOJ12H'

user = "Danny"

class Playlist:
    def __init__(self, source_file, reference):
        playlist = json.load(source_file)
        self.name = playlist["Playlist_URI"]
        self.tracks = playlist["Track_URIs"]
        self.reference = reference


    def __eq__(self, other):
        return self.name == other.name and self.tracks == other.tracks

    def sync(self):
        diff = [i for i in self.tracks if i not in self.reference.tracks]
        self.reference.tracks += diff
        return diff
    
    # dumps a playlist (class) to a file, just dumps the playlist and the ref, no updates is done
    def write_out(self):
        # todo messy code, but the only occurrance
        if self.reference == None:
            with open_playlist(self.name + "_ref", "w") as outfile:
                json.dump({"Playlist_URI":self.name, "Track_URIs":self.tracks}, outfile)
        with open_playlist(self.name, "w") as outfile:
            json.dump({"Playlist_URI":self.name, "Track_URIs":self.tracks}, outfile)
        if self.reference:
            self.reference.write_out()

class Drainlist:
    def __init__(self, source_file):
        drainlist = json.load(source_file)
        self.name = drainlist["Playlist_URI"]
        # these are source names
        source_names = list(set(drainlist["Sources"]))
        self.source_names = source_names
        self.sources = []
        if source_names:
            for name in source_names:
                self.add_source_init(name)


    def add_source(self, source_name):
        if source_name in self.source_names:
            return
        try:
            with open_playlist(source_name, "r") as source_file:
                with open_playlist(source_name  + "_ref", "r") as ref_file:
                    ref = Playlist(ref_file, None)
                    templist = Playlist(source_file, ref)
            self.sources += [templist]
            self.source_names += [i.name for i in [templist]]
        except:
            raise Exception("File not found")   

    def add_source_init(self, source_name):
        try:
            with open_playlist(source_name, "r") as source_file:
                with open_playlist(source_name  + "_ref", "r") as ref_file:
                    ref = Playlist(ref_file, None)
                    templist = Playlist(source_file, ref)
            self.sources += [templist]
        except:
            raise Exception("File not found")   


    def write_out(self):
        with open_playlist(self.name, "w+") as outfile:
            json.dump({"Playlist_URI":self.name, "Sources":self.source_names}, outfile)
        for s in self.sources:
            s.reference.write_out()
    
    # checks all sources for any songs to add, it then returns them and updates the references
    def sync(self):
        diff = set([])
        for source in self.sources:
            [diff.add(i) for i in source.sync()]
        return diff

    def cleanup(self, user):
        for source in self.sources:
            # todo the actual code
            filename = user + "/"  "Playlists" + "/" + source.name
            os.remove(filename)


            
def open_playlist(playlist_name, flag):
    return open(user + "/"  "Playlists" + "/" + playlist_name, flag)


def generate_drainlist(sources, destination_list):
        with open_playlist(destination_list, "w+") as outfile:
            json.dump({"Playlist_URI": destination_list, "Sources":sources}, outfile)







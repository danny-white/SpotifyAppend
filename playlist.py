import json
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

    def sync(self, reference):
        # if someone deletes something from their host playlist we want it to remain in the reference, 
        # we only care about things in self that are not in reference so that they can be added
        diff = [i for i in self.tracks if i not in reference.tracks]
        self.reference.tracks += diff
        return diff

class Drainlist:
    def __init__(self, source_file):
        drainlist = json.load(source_file)
        self.name = drainlist["Playlist_URI"]
        # these are source names
        source_names = list(set(drainlist["Sources"]))
        self.source_names = source_names[:]
        self.sources = []
        if source_names:
            for name in source_names:
                self.add_source(name)
    
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


    def update(self):
        # update the source 
        total_diff = set([])
        for source in self.sources:
            diff = source.sync(source.reference)
            if diff:
                for i in diff:
                    total_diff.add(i)
        return total_diff

    def write_out(self):
        with open_playlist(self.name, "w+") as outfile:
            return json.dump({"Playlist_URI":self.name, "Sources":self.source_names}, outfile)

            
def open_playlist(playlist_name, flag):
    return open(user + "/"  "Playlists" + "/" + playlist_name, flag)


Dlist = 0
with open_playlist("Drainlist", "r") as out:
    Dlist = Drainlist(out)
print("here")
Dlist.add_source(squaw_name)
Dlist.add_source(source_name)
Dlist.add_source(source_name)
Dlist.write_out()

#here but with










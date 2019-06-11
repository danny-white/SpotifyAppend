import json
import os
import spio


class Playlist:
    def __init__(self, user, name, tracks, reference):
        self.user = user
        self.name = name #name and URI are the same currently 
        self.tracks = tracks
        self.reference = reference

    @classmethod
    def from_file(cls, user, source_file, reference):
        playlist = json.load(source_file)
        name = playlist["Playlist_URI"]
        tracks = playlist["Track_URIs"]
        return cls(user, name, tracks, reference)

    @classmethod
    def from_web_api(cls, user, access_token, id, reference):
        tracks = spio.get_tracks(access_token, id)
        name = "spotify:playlist:" + id
        return cls(user, name, tracks, reference)

    def __eq__(self, other):
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        else:
            return self.name == other.name and self.tracks == other.tracks

    def sync(self):
        diff = [i for i in self.tracks if i not in self.reference.tracks]
        self.reference.tracks += diff
        return diff
    
    # dumps a playlist (class) to a file, just dumps the playlist and the ref, no updates are done
    def write_out(self):
        # todo messy code, but the only occurrance
        if self.reference:
            self.reference.write_out()
            with open_playlist(self.user, self.name, "w") as outfile:
                json.dump({"Playlist_URI":self.name, "Track_URIs":self.tracks}, outfile)
        else:
            with open_playlist(self.user, self.name + "_ref", "w") as outfile:
                json.dump({"Playlist_URI":self.name, "Track_URIs":self.tracks}, outfile) 


class Drainlist:
    def __init__(self, user, source_file):
        drainlist = json.load(source_file)
        self.user = user
        self.name = drainlist["Playlist_URI"]
        # these are source names
        self.source_names = list(set(drainlist["Sources"]))
        self.sources = []

        # if there are named sources add the proper playlist objects
        for name in self.source_names:
            try:
                self.add_source_init(name)
            except FileNotFoundError as e:
                id = e.filename.split(":")[2]
                self.add_source_api(id)


    def add_source(self, source_name):
        if source_name in self.source_names:
            return
        try:
            with open_playlist(self.user, source_name, "r") as source_file:
                with open_playlist(self.user, source_name  + "_ref", "r") as ref_file:
                    ref = Playlist.from_file(self.user, ref_file, None)
                    templist = Playlist.from_file(self.user, source_file, ref)
            self.sources += [templist]
            self.source_names += [i.name for i in [templist]]
        except:
            raise Exception("File not found")   

    def add_source_init(self, source_name):
        with open_playlist(self.user, source_name, "r") as source_file:
            with open_playlist(self.user, source_name  + "_ref", "r") as ref_file:
                ref = Playlist.from_file(self.user, ref_file, None)
                templist = Playlist.from_file(self.user, source_file, ref)
        self.sources += [templist]

    def add_source_api(self, id):
        ref = Playlist.from_web_api(self.user, spio.get_access_token(self.user), id, None)
        templist = Playlist.from_web_api(self.user, spio.get_access_token(self.user), id, ref)

        templist.write_out()
        ref.write_out()
        self.sources += [templist]


    def write_out(self):
        with open_playlist(self.user, self.name, "w+") as outfile:
            json.dump({"Playlist_URI":self.name, "Sources":self.source_names}, outfile)
        for s in self.sources:
            s.reference.write_out()
    
    # checks all sources for any songs to add, it then returns them and updates the references
    def sync(self):
        diff = set()
        for source in self.sources:
            [diff.add(i) for i in source.sync()]
        return diff

    def cleanup(self, user):
        for source in self.sources:
            filename = user + "/"  "Playlists" + "/" + source.name
            os.remove(filename)


            
def open_playlist(user, playlist_name, flag = "r"):
    return open(user + "/Playlists/" + playlist_name, flag)


def generate_drainlist(user, sources, destination_list):
        with open_playlist(user, destination_list, "w+") as outfile:
            json.dump({"Playlist_URI": destination_list, "Sources":sources}, outfile)





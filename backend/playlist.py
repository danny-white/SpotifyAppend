import json
import os
import spio


class Playlist:
    def __init__(self, user, name, uri, tracks, reference):
        """
        Creates a new Playlist object
        :param user: Associated user for this Playlist
        :param name: The Name of the playlist (a URI currently)
        :param tracks: The tracks of this Playlist
        :param reference: The reference playlist Object (None if this is a reference)
        """
        self.user = user
        self.name = name
        self.uri = uri
        self.tracks = tracks
        self.reference = reference

    @classmethod
    def from_file(cls, user, source_file, reference):
        """
        Generates a playlist object from a dumped file
        :param user: Associated user
        :param source_file: File to load the Playlist from
        :param reference: The reference playlist Object (None if this is a reference)
        :return: The newly constructed Playlist object
        """
        playlist = json.load(source_file)
        uri = playlist["Playlist_URI"]
        name = playlist["Name"]
        tracks = playlist["Track_URIs"]
        return cls(user, name, uri, tracks, reference)

    @classmethod
    def from_web_api(cls, user, access_token, uri, reference):
        """
        Generates a playlist object from a dumped file
        :param user: Associated user
        :param access_token:
        :param uri: the URI corresponding to the playlist
        :param reference: The reference playlist Object (None if this is a reference)
        :return: The newly constructed Playlist object
        """
        tracks = spio.get_tracks(access_token, uri)
        name = spio.get_name(access_token, uri)
        return cls(user, name, uri, tracks, reference)

    def __eq__(self, other):
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        else:
            return self.uri == other.uri and self.tracks == other.tracks

    def sync(self):
        """
        syncs a Playlist with its reference, adding any new track URI's to the reference
        :return: the URI's of all tracks in the Playlist that were not in the reference
        """
        diff = [i for i in self.tracks if i not in self.reference.tracks]
        self.reference.tracks += diff
        return diff
    
    def write_out(self):
        """
        Dumps a playlist object to a file, along with the reference
        :return: None
        """
        # todo messy code, but the only occurrance
        if self.reference:
            self.reference.write_out()
            with open_playlist(self.user, self.uri, "w") as outfile:
                json.dump({"Name": self.name, "Playlist_URI":self.uri, "Track_URIs":self.tracks}, outfile)
        else:
            with open_playlist(self.user, self.uri + "_ref", "w") as outfile:
                json.dump({"Name": self.name, "Playlist_URI":self.uri, "Track_URIs":self.tracks}, outfile)


class Drainlist:
    def __init__(self, user, source_file):
        """
        Generates a new Drainlist object for the given user
        :param user: Associated user
        :param source_file: File Drainlist is loaded from
        """
        drainlist = json.load(source_file)
        self.user = user
        self.name = drainlist["Name"]
        self.uri = drainlist["Playlist_URI"]
        # todo can this be a set?
        self.source_names = list(set([s["Name"] for s in drainlist["Sources"]]))
        self.source_uris = list(set([s["URI"] for s in drainlist["Sources"]]))
        self.sources = []

        # if there are named sources add the proper playlist objects
        for name in self.source_uris:
            try:
                self.add_source_file(name)
            except FileNotFoundError as e:
                uri = e.filename.split("/")[-1]
                self.add_source_api(uri)

    def add_source_file(self, source_name):
        """
        Adds a new Playlist source to a drainlist by filename (Playlist URI)
        fails if source and reference files do not exist
        :param source_name: Playlist filename (Playlist URI)
        :return: None
        """
        with open_playlist(self.user, source_name, "r") as source_file:
            with open_playlist(self.user, source_name  + "_ref", "r") as ref_file:
                ref = Playlist.from_file(self.user, ref_file, None)
                templist = Playlist.from_file(self.user, source_file, ref)
        self.sources += [templist]

    def remove_source(self, source_name):
        """
        Removes all Source from the Drainlist that match the given name
        :param source_name: Name of Source PLaylists to remove (one name, but can remove multiple)
        :return: None
        """
        toRem = None
        for source in self.sources:
            if source.uri == source_name:
                toRem = source
        if toRem:
            self.sources.remove(toRem)

    def add_source_api(self, uri):
        """
        Adds a new Playlist source to a drainlist via the API using the Playlist URI
        :param uri: URI of the playlist to be added
        :return: None
        """
        # here if source file does not exist, but still
        try:
            refFile = open_playlist(self.user, uri + "_ref")
            ref = Playlist.from_file(self.user, refFile, None)
        except Exception as e:
            ref = Playlist.from_web_api(self.user, spio.get_access_token(self.user), uri, None)
        templist = Playlist.from_web_api(self.user, spio.get_access_token(self.user), uri, ref)

        templist.write_out()
        ref.write_out()
        self.sources += [templist]

    def populate(self, access_token):
        """
        Adds one of each track (uniquely) in every source to the drainlist sink on Spotify
        it will not add tracks already on the playlist
        This should only be done on startup in order to skip the ref stage, can remove later
        :param access_token: Securely ID's the user
        :return: None
        """
        tracks = []
        for source in self.sources:
            tracks += source.tracks
        tracks = list(set(tracks) - set(spio.get_tracks(access_token, self.uri)))
        spio.add_tracks_to_drain(access_token, self, list(set(tracks)))

    def depopulate(self, access_token):
        """
        Deletes all tracks from the drainlist sink on spotify
        :param access_token: Securely ID's the user
        :return: None
        """
        tracks = []
        for source in self.sources:
            tracks += set(source.tracks)
        spio.remove_tracks_from_drain(access_token, self, tracks)

    def write_out(self):
        """
        Dumps drainlist all sources and all references to disk
        :return: None
        """
        with open_drainlist(self.user, self.uri, "w+") as outfile:
            json.dump({"Playlist_URI":self.uri, "Sources": spio.print_sources(self.sources)}, outfile)
        for s in self.sources:
            s.reference.write_out()
    

    def sync(self):
        """
        Syncs all sources, leaving references updated to include new Tracks
        returns new tracks (to be uploaded immediately after)
        :return: list of Track uri's returned by each sources syncing
        """
        diff = set()
        for source in self.sources:
            [diff.add(i) for i in source.sync()]
        return diff

    def cleanup(self, user):
        """
        Deletes written out source files, references are all that is stored long term
        this should be changed to allow for direct comparison from in memory plists against
        file references
        :param user:
        :return:
        """
        for source in self.sources:
            filename = user + "/"  "Playlists" + "/" + source.uri
            os.remove(filename)
            
def open_playlist(user, playlist_name, flag = "r"):
    return open(user + "/Playlists/" + playlist_name, flag)

def open_drainlist(user, playlist_name, flag = "r"):
    return open_playlist(user, playlist_name + "_drain", flag)

def open_reflist(user, playlist_name, flag = "r"):
    return open_playlist(user, playlist_name + "_ref", flag)


def generate_drainlist(user, sources, destination_list):
        with open_playlist(user, destination_list, "w+") as outfile:
            json.dump({"Playlist_URI": destination_list, "Sources":sources}, outfile)





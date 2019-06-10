# Makes importing spotify and playlist easier
import sys, os
sys.path.append('..')

import unittest

import spotify
import playlist

test_user = "Test_User"

# drainlist_text = 

class TestSpotifyMethods(unittest.TestCase):

# todo unsure how best to do auth code tests
# also token code, for now it works, so don't touch it
    def test_write_out(self):
        user = test_user
        name, uri = "TEST1", "TEST1"
        tracks = ["t1", "t2", "t3"]

        # write out a fake playlist and reference
        spotify.write_out_tracklist(user, name, uri, tracks)
        self.assertTrue(os.path.exists(user + "/Playlists/" + name))
        self.assertTrue(os.path.exists(user + "/Playlists/" + name + "_ref"))

        
        # update the reference
        new_tracks = ["t4","t5","t6"]
        spotify.write_out_tracklist(user, name, uri, new_tracks)

        # test to ensure the reference was not updated, but the 
        # playlist was
        with spotify.open_playlist(user, name) as infile:   
            for line in infile:
                for t in new_tracks:
                    self.assertTrue(t in line)
                for t in tracks:
                    self.assertFalse(t in line)
        with spotify.open_playlist(user, name + "_ref") as infile:   
            for line in infile:
                for t in tracks:
                    self.assertTrue(t in line)
                for t in new_tracks:
                    self.assertFalse(t in line)
        os.remove(test_user + "/Playlists/TEST1")
        os.remove(test_user + "/Playlists/TEST1_ref")
    
    def test_list_drains(self):
        self.assertEqual(spotify.list_drains(test_user), ["test_drain"])

    def test_create_new_drain(self):
        new_drainlist = "new_drainlist"
        playlist_uris = ["p3,p4,p5"]
        spotify.create_new_drain(test_user, new_drainlist, playlist_uris)
        with spotify.open_playlist(test_user, new_drainlist + "_drain") as infile:   
            for line in infile:
                self.assertTrue(all([plist in line for plist in playlist_uris]))
        os.remove(test_user + "/Playlists/new_drainlist_drain")

    # write Drainlist and Playlist class tests
class TestPlaylistMethods(unittest.TestCase):
    refname = "test_playlist_ref"
    listname = "test_playlist"
    ref, plist = None, None
    with playlist.open_playlist(test_user, refname, "r") as infile:
        ref = playlist.Playlist.from_file(test_user,infile, None)
    with playlist.open_playlist(test_user, listname, "r") as infile:
        plist = playlist.Playlist.from_file(test_user, infile, ref)
    
    def test_sync(self):
        self.assertEqual(self.plist.sync(), ["spotify:track:t3"])
        self.assertEqual(self.ref.tracks, self.plist.tracks)

    def test_write_out(self):
        import copy
        plist2 = copy.copy(self.plist)
        plist2.name = "test2"
        plist2.reference.name = "test2"
        plist2.write_out()

        with spotify.open_playlist(test_user, "test2") as infile:
            for line in infile:
                self.assertTrue(all([i in line for i in ["t1","t2","t3"]]))
        with spotify.open_playlist(test_user, "test2_ref") as infile:
            for line in infile:
                self.assertTrue(all([i in line for i in ["t1","t2","t3"]]))

        os.remove(test_user + "/Playlists/" + "test2")
        os.remove(test_user + "/Playlists/" + "test2_ref")
class TestDrainlistMethods(unittest.TestCase):
    Dlist = None
# todo the rest of this
    def setUp(self):
        with spotify.open_playlist(test_user, "test_drain") as infile:
            Dlist = playlist.Drainlist(test_user, infile)
    def test_add_source(self):
        self.assertEqual(1,1)
        print(Dlist)
        

    # def add_source_init(self):

    # def write_out(self):

    # def sync(self):

    # def cleanup(self):

class IntegrationTests(unittest.TestCase):
    spotify.initialize()
    spotify.get_playlists()

if __name__ == '__main__':
    unittest.main()

# setup and teardown are within a single class, they bookend each test in that class
# setupclass and teardownclass this bookends an entire test class
# time to write a dickload of unittest, put the folders and files in a test folder / don't actually poke spotify, just mock that out, since it'll work

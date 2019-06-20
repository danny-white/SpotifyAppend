# Makes importing spotify and playlist easier
import sys, os
sys.path.append('..')

import unittest

import spotify
import spio
import playlist

test_user = "Test_User"
# dummy lists
test_drain = "{\"Playlist_URI\": \"spotify:playlist:test_drain\", \"Sources\": [\"spotify:playlist:test_playlist\", \"spotify:playlist:test_playlist2\"]}"
test_playlist = "{\"Playlist_URI\": \"spotify:playlist:test_playlist\", \"Track_URIs\": [\"spotify:track:t1\", \"spotify:track:t2\", \"spotify:track:t3\"]}"
test_playlist_ref = "{\"Playlist_URI\": \"spotify:playlist:test_playlist\", \"Track_URIs\": [\"spotify:track:t1\", \"spotify:track:t2\"]}"

# actual lists for testing
test_playlist2 = "{\"Playlist_URI\": \"spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb\", \"Track_URIs\": [\"spotify:track:6koWevx9MqN6efQ6qreIbm\", \"spotify:track:7EE7jbv7Dv8ZkyWBlKhPXX\", \"spotify:track:1zTmKEtaxIqi2ByGBLmI3s\", \"spotify:track:1RjP07A2H4WMmozQidd9x7\", \"spotify:track:0dE9ro91KUtV5Xi7bDPy6b\", \"spotify:track:1UYXdZZMnCrlUqDRuIs9OE\", \"spotify:track:18rXOovmohAMcFwUPAUAN2\", \"spotify:track:3DERgYjztCL6oME2fvRl6z\", \"spotify:track:0TRbihonM8LyyQ7OClspEy\", \"spotify:track:5MbUyUE6erY9mVgXaecQwR\", \"spotify:track:0Mx2W2i58sIPmEvfKdh1Q2\", \"spotify:track:52FCSkVx41xDQ3oCjHIeNJ\", \"spotify:track:7hjJKZwcW0vze3A48dqcCr\", \"spotify:track:08Z3vnfucOMerexVE2RR8w\", \"spotify:track:4FqfG6WnkXEMc6ZZ58lJWb\", \"spotify:track:7Jzr0HLMMvTOo9Xvc8EjZL\", \"spotify:track:3nV9CwvpCHGd9fvJ1pn185\", \"spotify:track:1eueYfJA1ADnfghW90xxxf\", \"spotify:track:4cx6srR6OQzmd6mzpeaQsY\", \"spotify:track:5WwaKGBmg0TpG8mRQpksl2\", \"spotify:track:1wJCpDiJeQccXuNguS8umH\", \"spotify:track:78qM62MHvNxFJLpShqmq28\", \"spotify:track:5EeNRe6Fi29tTrssVzl4dw\", \"spotify:track:3Lr9aRWF57Dd8NsjeWTKNp\", \"spotify:track:1Z5GCYgzsBxb9VUUVQRG2E\", \"spotify:track:74fNA9uOtYFbkpG7gE8AKV\", \"spotify:track:5DQEWQoJ3deYCPkRIFm3Ci\", \"spotify:track:7dYXMe7VAmmkKDyGByUOfM\", \"spotify:track:3ozCQsJ9IA0v3ZlpE21UzK\", \"spotify:track:71CRvX5TW0CsiCxGZ00IfA\"]}"
test_playlist2_ref = test_playlist2[:]
test_playlist3 = "{\"Playlist_URI\": \"spotify:playlist:6E2XjEeEOEhUKVoftRHusb\", \"Track_URIs\": [\"spotify:track:2qOm7ukLyHUXWyR4ZWLwxA\", \"spotify:track:4MbV8zrWudQflnbiIzp29t\", \"spotify:track:3MQmQowCMVhepBDEsuBXIm\", \"spotify:track:63BokRfXSQhEU6Qi2dSJpZ\", \"spotify:track:0WKYRFtH6KKbaNWjsxqm70\", \"spotify:track:503OTo2dSqe7qk76rgsbep\", \"spotify:track:2C3QwVE5adFCVsCqayhPW7\", \"spotify:track:2g8HN35AnVGIk7B8yMucww\", \"spotify:track:0HOqINudNgQFpg1le5Hnqe\", \"spotify:track:2Ih217RCGAmyQR68Nn7Cqo\"]}"
test_playlist3_ref = test_playlist3[:]
test_drain2 = "{\"Playlist_URI\": \"spotify:playlist:069rrIb9s1MRw2BBwXmeJE\", \"Sources\": [\"spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb\", \"spotify:playlist:6E2XjEeEOEhUKVoftRHusb\"]}"

dname = "spotify:playlist:069rrIb9s1MRw2BBwXmeJE"
listname = "spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb"
refname = "spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb_ref"

list2name = "spotify:playlist:6E2XjEeEOEhUKVoftRHusb"
ref2name = "spotify:playlist:6E2XjEeEOEhUKVoftRHusb_ref"

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
        with playlist.open_playlist(user, name) as infile:
            for line in infile:
                for t in new_tracks:
                    self.assertTrue(t in line)
                for t in tracks:
                    self.assertFalse(t in line)
        with playlist.open_playlist(user, name + "_ref") as infile:
            for line in infile:
                for t in tracks:
                    self.assertTrue(t in line)
                for t in new_tracks:
                    self.assertFalse(t in line)
        os.remove(test_user + "/Playlists/TEST1")
        os.remove(test_user + "/Playlists/TEST1_ref")
    
    def test_list_drains(self):
        drain_name = "test_drain"
        with playlist.open_playlist(test_user, drain_name, "w+") as outfile:
            outfile.write(test_playlist_ref)
        self.assertEqual(spotify.list_drains(test_user), ["test_drain"])
        os.remove(test_user + "/Playlists/" + drain_name)

    def test_create_new_drain(self):
        new_drainlist = "new_drainlist"
        playlist_uris = ["p3,p4,p5"]
        spotify.create_new_drain(test_user, new_drainlist, playlist_uris)
        with playlist.open_playlist(test_user, new_drainlist) as infile:
            for line in infile:
                self.assertTrue(all([plist in line for plist in playlist_uris]))
        os.remove(test_user + "/Playlists/new_drainlist")





    # write Drainlist and Playlist class tests
class TestPlaylistMethods(unittest.TestCase):
    refname = "test_playlist_ref"
    listname = "test_playlist"

    with playlist.open_playlist(test_user, refname, "w+") as outfile:
        outfile.write(test_playlist_ref)
    with playlist.open_playlist(test_user, listname, "w+") as outfile:
        outfile.write(test_playlist)

    with playlist.open_playlist(test_user, refname, "r") as infile:
        ref = playlist.Playlist.from_file(test_user,infile, None)
    with playlist.open_playlist(test_user, listname, "r") as infile:
        plist = playlist.Playlist.from_file(test_user, infile, ref)

    os.remove(test_user + "/Playlists/" + refname)
    os.remove(test_user + "/Playlists/" + listname)
    
    def test_sync(self):
        self.assertEqual(self.plist.sync(), ["spotify:track:t3"])
        self.assertEqual(self.ref.tracks, self.plist.tracks)

    def test_write_out(self):
        import copy
        plist2 = copy.copy(self.plist)
        plist2.name = "test2"
        plist2.reference.name = "test2"
        plist2.write_out()

        with playlist.open_playlist(test_user, "test2") as infile:
            for line in infile:
                self.assertTrue(all([i in line for i in ["t1","t2","t3"]]))
        with playlist.open_playlist(test_user, "test2_ref") as infile:
            for line in infile:
                self.assertTrue(all([i in line for i in ["t1","t2","t3"]]))

        os.remove(test_user + "/Playlists/" + "test2")
        os.remove(test_user + "/Playlists/" + "test2_ref")

class TestDrainlistMethods(unittest.TestCase):

    def setUp(self):
        with playlist.open_playlist(test_user, refname, "w+") as outfile:
            outfile.write(test_playlist2_ref)
        with playlist.open_playlist(test_user, listname, "w+") as outfile:
            outfile.write(test_playlist2)
        with playlist.open_playlist(test_user, ref2name, "w+") as outfile:
            outfile.write(test_playlist3_ref)
        with playlist.open_playlist(test_user, list2name, "w+") as outfile:
            outfile.write(test_playlist3)
        with playlist.open_playlist(test_user, dname, "w+") as outfile:
            outfile.write(test_drain2)

    def tearDown(self):
        for f in os.listdir(test_user + "/Playlists/"):
            os.remove(test_user + "/Playlists/" + f)

    def test_add_source_init(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)
        d.remove_source(list2name)
        d.add_source_init(list2name)
        self.assertEqual(set([s.name for s in d.sources]), {listname, list2name})

    def test_remove_source(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)
        d.remove_source(list2name)
        self.assertEqual(set([s.name for s in d.sources]), {listname})

    def add_source_api(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)
        d.remove_source(list2name)
        d.add_source_init(list2name)
        self.assertEqual(set([s.name for s in d.sources]), {listname, list2name})

    def test_init(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)

        self.assertEqual(d.user, test_user)
        self.assertEqual(d.name, dname)
        self.assertEqual(set(d.source_names), {listname, list2name})
        self.assertEqual({s.name for s in d.sources}, {listname, list2name})

    def test_populate_depopulate(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)

        token = spio.get_access_token(test_user)
        tracks = spio.get_tracks(token, listname) + spio.get_tracks(token, list2name)
        d.populate(token)
        self.assertEqual(set(tracks), set(spio.get_tracks(token, d.name)))
        d.depopulate(token)
        self.assertEqual(set(), set(spio.get_tracks(token, d.name)))

    def test_write_out(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)
        d.write_out()
        with playlist.open_playlist(test_user, dname) as infile:
            data = infile.read()
        self.assertTrue(listname in data)
        self.assertTrue(list2name in data)
        self.assertTrue(dname in data)


    def test_sync(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)
        self.assertEqual(set(), d.sync())


    def test_cleanup(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)
        expected_files = ['spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb', 'spotify:playlist:6E2XjEeEOEhUKVoftRHusb',
         'spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb_ref', 'spotify:playlist:069rrIb9s1MRw2BBwXmeJE',
         'spotify:playlist:6E2XjEeEOEhUKVoftRHusb_ref']

        self.assertEqual(set(os.listdir(test_user + "/Playlists/")), set(expected_files))
        d.cleanup(test_user)

        expected_files = ['spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb_ref', 'spotify:playlist:069rrIb9s1MRw2BBwXmeJE',
         'spotify:playlist:6E2XjEeEOEhUKVoftRHusb_ref']

        self.assertEqual(set(os.listdir(test_user + "/Playlists/")), set(expected_files))

class TestSpioMethdods(unittest.TestCase):
    token = spio.get_access_token(test_user)

    def setUp(self):
        with playlist.open_playlist(test_user, refname, "w+") as outfile:
            outfile.write(test_playlist2_ref)
        with playlist.open_playlist(test_user, listname, "w+") as outfile:
            outfile.write(test_playlist2)
        with playlist.open_playlist(test_user, ref2name, "w+") as outfile:
            outfile.write(test_playlist3_ref)
        with playlist.open_playlist(test_user, list2name, "w+") as outfile:
            outfile.write(test_playlist3)
        with playlist.open_playlist(test_user, dname, "w+") as outfile:
            outfile.write(test_drain2)

    def tearDown(self):
        for f in os.listdir(test_user + "/Playlists/"):
            os.remove(test_user + "/Playlists/" + f)


    def test_get_playlists(self):
        lists = spio.get_playlists(self.token)
        self.assertTrue(listname in [plist["uri"] for plist in lists])
        self.assertTrue(list2name in [plist["uri"] for plist in lists])
        self.assertTrue(dname in [plist["uri"] for plist in lists])

    def test_get_tracks(self):
        # since playlist is volatile just check if one track is in there
        tracks = spio.get_tracks(self.token, listname)
        self.assertTrue("spotify:track:7EE7jbv7Dv8ZkyWBlKhPXX" in tracks)

    def test_add_remove_tracks_to_from_drain(self):
        with playlist.open_playlist(test_user, dname) as infile:
            d = playlist.Drainlist(test_user, infile)
        dump_tracks = ["spotify:track:7EE7jbv7Dv8ZkyWBlKhPXX"]
        spio.add_tracks_to_drain(self.token, d, dump_tracks)
        tracks = spio.get_tracks(self.token, d.name)
        self.assertEqual(tracks, dump_tracks)
        spio.remove_tracks_from_drain(self.token, d, dump_tracks)
        spio.get_tracks(self.token, d.name)
        tracks = spio.get_tracks(self.token, d.name)
        self.assertEqual(tracks, [])

    def test_create_playlist(self):
        spio.create_playlists(spio.get_access_token(test_user), "test")
        print(1)

    def test_remove_tracks_from_drain(self):
        1
#     todo also token code


class IntegrationTests(unittest.TestCase):
    drain_name = "spotify:playlist:069rrIb9s1MRw2BBwXmeJE"
    sources = ["4L3PeQ9LzinSq0Q3KnzLvb", "6E2XjEeEOEhUKVoftRHusb"]
    tracks = ['spotify:track:6koWevx9MqN6efQ6qreIbm', 'spotify:track:7EE7jbv7Dv8ZkyWBlKhPXX',
              'spotify:track:1zTmKEtaxIqi2ByGBLmI3s', 'spotify:track:1RjP07A2H4WMmozQidd9x7',
              'spotify:track:0dE9ro91KUtV5Xi7bDPy6b', 'spotify:track:1UYXdZZMnCrlUqDRuIs9OE',
              'spotify:track:18rXOovmohAMcFwUPAUAN2', 'spotify:track:3DERgYjztCL6oME2fvRl6z',
              'spotify:track:0TRbihonM8LyyQ7OClspEy', 'spotify:track:5MbUyUE6erY9mVgXaecQwR',
              'spotify:track:0Mx2W2i58sIPmEvfKdh1Q2', 'spotify:track:52FCSkVx41xDQ3oCjHIeNJ',
              'spotify:track:7hjJKZwcW0vze3A48dqcCr', 'spotify:track:08Z3vnfucOMerexVE2RR8w',
              'spotify:track:4FqfG6WnkXEMc6ZZ58lJWb', 'spotify:track:7Jzr0HLMMvTOo9Xvc8EjZL',
              'spotify:track:3nV9CwvpCHGd9fvJ1pn185', 'spotify:track:1eueYfJA1ADnfghW90xxxf',
              'spotify:track:4cx6srR6OQzmd6mzpeaQsY', 'spotify:track:5WwaKGBmg0TpG8mRQpksl2',
              'spotify:track:1wJCpDiJeQccXuNguS8umH', 'spotify:track:78qM62MHvNxFJLpShqmq28',
              'spotify:track:5EeNRe6Fi29tTrssVzl4dw', 'spotify:track:3Lr9aRWF57Dd8NsjeWTKNp',
              'spotify:track:1Z5GCYgzsBxb9VUUVQRG2E', 'spotify:track:74fNA9uOtYFbkpG7gE8AKV',
              'spotify:track:5DQEWQoJ3deYCPkRIFm3Ci', 'spotify:track:7dYXMe7VAmmkKDyGByUOfM',
              'spotify:track:3ozCQsJ9IA0v3ZlpE21UzK', 'spotify:track:71CRvX5TW0CsiCxGZ00IfA',
              'spotify:track:2qOm7ukLyHUXWyR4ZWLwxA', 'spotify:track:4MbV8zrWudQflnbiIzp29t',
              'spotify:track:3MQmQowCMVhepBDEsuBXIm', 'spotify:track:63BokRfXSQhEU6Qi2dSJpZ',
              'spotify:track:0WKYRFtH6KKbaNWjsxqm70', 'spotify:track:503OTo2dSqe7qk76rgsbep',
              'spotify:track:2C3QwVE5adFCVsCqayhPW7', 'spotify:track:2g8HN35AnVGIk7B8yMucww',
              'spotify:track:0HOqINudNgQFpg1le5Hnqe', 'spotify:track:2Ih217RCGAmyQR68Nn7Cqo']
    def setUp(self):
        spotify.create_new_drain(test_user, self.drain_name, self.sources)
        self.access_token = spio.get_access_token(test_user)
        with playlist.open_playlist(test_user, self.drain_name) as infile:
            self.Dlist = playlist.Drainlist(test_user, infile)

        if spio.get_tracks(self.access_token, self.Dlist.name):
            self.Dlist.depopulate(spio.get_access_token(test_user))
    def tearDown(self):
        for f in os.listdir(test_user + "/Playlists/"):
            os.remove(test_user + "/Playlists/" + f)

        if spio.get_tracks(self.access_token, self.Dlist.name):
            self.Dlist.depopulate(spio.get_access_token(test_user))
    def test_integ_populate_and_sync(self):

        # drop a track
        dropped_track = self.Dlist.sources[0].reference.tracks.pop()
        self.Dlist.sources[0].tracks.remove(dropped_track)

        # populate
        self.Dlist.populate(self.access_token)
        tracks = self.tracks[:]
        tracks.remove(dropped_track)
        self.assertEqual(set(tracks), set(spio.get_tracks(self.access_token, self.Dlist.name)))

        # re-add the track and sync
        self.Dlist.sources[0].tracks += [dropped_track]
        diff = self.Dlist.sync()
        spio.add_tracks_to_drain(self.access_token, self.Dlist, diff)

        # check if the track was added
        tracks += [dropped_track]
        self.assertEqual(set(tracks), set(spio.get_tracks(self.access_token, self.Dlist.name)))
        # depopulate
        self.Dlist.depopulate(spio.get_access_token(test_user))
        self.assertEqual(set(), set(spio.get_tracks(self.access_token, self.Dlist.name)))

        self.Dlist.cleanup(test_user)
        self.assertEqual(set(os.listdir(test_user + "/Playlists/")), {'spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb_ref', 'spotify:playlist:069rrIb9s1MRw2BBwXmeJE', 'spotify:playlist:6E2XjEeEOEhUKVoftRHusb_ref'})

class WebRequestTests(unittest.TestCase):
    # todo this class will test entire behavior for frontend entrypoints
    # take in plaintext representing the request data and proceed from there,
    # piggybacks on the rest of the methods working
    1


if __name__ == '__main__':
    unittest.main()
    # print(spio.get_access_token(test_user))

# setup and teardown are within a single class, they bookend each test in that class
# setupclass and teardownclass this bookends an entire test class
# time to write a dickload of unittest, put the folders and files in a test folder / don't actually poke spotify, just mock that out, since it'll work

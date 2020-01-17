import sys, os
sys.path.append('..')

import unittest

import spotify
import spio
import playlist

test_user = "Test_User"

class IntegrationTests(unittest.TestCase):
    drainSinkName = "drainSink"
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
        spotify.create_new_drain(test_user, self.drainSinkName ,self.drain_name, self.sources)
        self.access_token = spio.get_access_token(test_user)
        with playlist.open_drainlist(test_user, self.drain_name) as infile:
            self.Dlist = playlist.Drainlist(test_user, infile)

        if spio.get_tracks(self.access_token, self.Dlist.uri):
            self.Dlist.depopulate(spio.get_access_token(test_user))
    def tearDown(self):
        for f in os.listdir(test_user + "/Playlists/"):
            os.remove(test_user + "/Playlists/" + f)

        if spio.get_tracks(self.access_token, self.Dlist.uri):
            self.Dlist.depopulate(spio.get_access_token(test_user))
    def test_integ_populate_and_sync(self):

        # drop a track
        dropped_track = self.Dlist.sources[0].reference.tracks.pop()
        self.Dlist.sources[0].tracks.remove(dropped_track)

        # populate
        self.Dlist.populate(self.access_token)
        tracks = self.tracks[:]
        tracks.remove(dropped_track)
        self.assertEqual(set(tracks), set(spio.get_tracks(self.access_token, self.Dlist.uri)))

        # re-add the track and sync
        self.Dlist.sources[0].tracks += [dropped_track]
        diff = self.Dlist.sync()
        spio.add_tracks_to_drain(self.access_token, self.Dlist, diff)

        # check if the track was added
        tracks += [dropped_track]
        self.assertEqual(set(tracks), set(spio.get_tracks(self.access_token, self.Dlist.uri)))
        # depopulate
        self.Dlist.depopulate(spio.get_access_token(test_user))
        self.assertEqual(set(), set(spio.get_tracks(self.access_token, self.Dlist.uri)))

        self.Dlist.cleanup(test_user)
        self.assertEqual(set(os.listdir(test_user + "/Playlists/")), {'spotify:playlist:4L3PeQ9LzinSq0Q3KnzLvb_ref', 'spotify:playlist:069rrIb9s1MRw2BBwXmeJE_drain', 'spotify:playlist:6E2XjEeEOEhUKVoftRHusb_ref'})

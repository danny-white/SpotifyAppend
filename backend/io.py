import requests
####################################
######## Spotify IO Code  ########## 
####################################


# get's a list of playlists for the current user
# todo you can remove this, and instead source based 
# on the names in the drainlist
def get_playlists(access_token):
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + access_token}
    requests.get(url=url, headers=headers) 
    try:
        all_playlists = requests.get(url=url, headers=headers).json()
        return all_playlists["items"]
    except:
        print("unable to acquire playlist list")

#todo dont need this, if you have a playlist uri just get the tracks directly ya dip
def get_playlist(access_token, uri="6E2XjEeEOEhUKVoftRHusb"): #defaults to nursultan bulletakbay
    url = "https://api.spotify.com/v1/playlists/" + uri
    headers = {"Authorization": "Bearer " + access_token}
    requests.get(url=url, headers=headers)
    try:
        playlist = requests.get(url=url, headers=headers).json()
        return playlist
    except:
        print("unable to acquire playlist")


# Takes a playlist id, (not URI) and returns the list of track uri's
def get_tracks(playlist_uri = "6E2XjEeEOEhUKVoftRHusb"):
    ret = []
    url = "https://api.spotify.com/v1/playlists/" + playlist_uri + "/tracks"
    headers = {"Authorization": "Bearer " + access_token}
    hasNext = 1
    while hasNext:
        tracks = requests.get(url=url, headers=headers)
        jsonTrack = tracks.json()
        ret += [jsonTrack["items"][i]["track"]["uri"] for i in range(len(jsonTrack["items"]))]
        hasNext = jsonTrack["next"]
        url = jsonTrack["next"]
    return ret

# takes a list of tracks and a drainlist object and appends the tracks to the drainlist
# args: drainlist = drainlist object that is having tracks added
#       tracks = tracks to be added in a list
def add_tracks_to_drain(access_token, drainlist, tracks):
    track_list = split_list(tracks, 100) 
    # if there are no tracks this is still an empty list, iterate through split list and upload
    for tracks in track_list:
        trackstring = generate_uri_string(tracks)
        url = "https://api.spotify.com/v1/playlists/%s/tracks?uris=%s" % (drainlist.name.split(":")[2], trackstring)
        headers = {"Authorization": "Bearer " + access_token}
        retVal = requests.post(url=url, headers=headers)
    else:
        return "no tracks"

####################################
###### End Spotify IO Code  ######## 
####################################
print(get_playlists("A"))
get_playlist()
get_tracks()
import requests, base64, time
import json

myUrl = "http://127.0.0.1:5000/"
cwd = "/Users/Danny/Documents/CS/SpotifyAppend/backend"
sec = []
with open(cwd + "/Secrets", "r") as infile:
    for line in infile:
        sec.append(line.strip())
client_id = sec[0]
client_secret= sec[1]


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
def get_playlist(access_token, id="6E2XjEeEOEhUKVoftRHusb"): #defaults to nursultan bulletakbay
    url = "https://api.spotify.com/v1/playlists/" + id
    headers = {"Authorization": "Bearer " + access_token}
    requests.get(url=url, headers=headers)
    try:
        playlist = requests.get(url=url, headers=headers).json()
        return playlist
    except:
        print("unable to acquire playlist")


# Takes a playlist id, (not URI) and returns the list of track uri's
def get_tracks(access_token, playlist_id="6E2XjEeEOEhUKVoftRHusb"):
    ret = []
    url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
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


####################################
########### Utilities  #############
####################################

# splits a list into sublists of len splitsize, last sublist may be smaller if
# not enough elements are present (no padding)
def split_list(tracks, splitsize):
    tracks =  list(tracks)
    end = splitsize
    ret = []
    front = 0
    while (front < len(tracks)):
        ret += [tracks[front:end]]
        front = end
        end = min(len(tracks), end + splitsize)
    return ret

# changes a list of tracks into a properly formatted uri string for bulk loads
def generate_uri_string(tracks):
    return "%2C".join(tracks)






####################################
###### Token Handling Code #########
####################################

##### User Interaction Token Code #####
# todo UI token code will be moved back to spotify.py or into another file
# backend Token code =/= frontend token code, for the backend if the tokens are hosed
# just give up and cry
def get_tokens_from_code(code):
    url = "https://accounts.spotify.com/api/token/"
    params = {"grant_type" :"authorization_code", "code" : code, "redirect_uri":myUrl + "authentication_return"}
    headers = make_authorization_headers(client_id, client_secret)
    return requests.post(url=url, data=params, headers=headers)

# Builds the Authentication URL and redirects the user there, so more tokens can be gathered
def get_new_tokens():
    url = "https://accounts.spotify.com/authorize/"
    scopes = "playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative user-follow-read"
    params = { "client_id":client_id, "response_type":"code", "redirect_uri": myUrl + "authentication_return", "scope":scopes}
    a = requests.get(url=url, params=params)
    return a

##### End User Interaction Token Code #####

def get_access_token(user):
    # access the users token file
    with tokenfile_open(user) as tokenfile:
        tokens = json.load(tokenfile)
    # if DNE then allow FNF exception to propogate
    # if FNF then we need intervention to get new tokens which is out of scope for this file

    # if the file is aged out then refresh and update the file
    if tokens["expires_at_epoch"] < int(time.time()) + 60 * 5:
        access_token , ttl = refresh_tokens(user)
        tokens["access_token"] = access_token
        tokens["expires_at_epoch"] = ttl + int(time.time())
        with tokenfile_open(user, "w+") as tokenfile:
            json.dump(tokens, tokenfile)

    # finally return the token
    return tokens["access_token"]

def get_refresh_token(user):
    with tokenfile_open(user) as tokenfile:
        tokens = json.load(tokenfile)
    return tokens["refresh_token"]


# PURE SPOTIFY API CALL
def refresh_tokens(user):
    url = "https://accounts.spotify.com/api/token/"
    data = {"grant_type" : "refresh_token", "refresh_token" : get_refresh_token(user)}
    headers = make_authorization_headers(client_id, client_secret)
    resp = requests.post(url=url, data = data, headers = headers).json()
    return resp["access_token"], resp["expires_in"]

def tokenfile_open(user, flag="r"):
    return open(user + "/" + user + "_tokens", flag)

def make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(str(client_id + ':' + client_secret).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

####################################
#### End Token Handling Code #######
####################################



####################################
######### End Utilities  ###########
####################################
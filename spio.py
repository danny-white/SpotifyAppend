import requests, base64, time, os
import json

# put this in the DB as well NO GLOBALS!
myUrl = "http://127.0.0.1:5000/"
cwd = "/Users/Danny/Documents/CS/SpotifyAppend/backend"
uri_header = "spotify:playlist:"
sec = [] # Secrets can be put in the db secrets table
with open(cwd + "/Secrets", "r") as infile:
    for line in infile:
        sec.append(line.strip())
client_id = sec[0]
client_secret= sec[1]


####################################
######## Spotify IO Code  ########## 
####################################


def get_playlists(access_token):
    """
    Returns the playlists followed by a user
    :param access_token: determines the user to edit securely
    :return: all playlists followed by the user (list of dictionaries)
    """
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + access_token}
    requests.get(url=url, headers=headers)
    try:
        all_playlists = requests.get(url=url, headers=headers).json()
        return all_playlists["items"]
    except:
        print("unable to acquire playlist list")

def create_playlists(access_token, name):
    """
    Creates a new playlist for the user to follow
    :param access_token: securely determines the user
    :param name: name for the new playlist
    :return: URI of the newly generated playlist
    """
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + access_token}
    resp = requests.post(url=url, data=json.dumps({"name":name}), headers=headers)
    r = json.loads(resp.text)
    return r["uri"]

def get_name(access_token, uri):
    id = uri.split(":")[2]
    url = "https://api.spotify.com/v1/playlists" + "/" + id
    headers = {"Authorization": "Bearer " + access_token}
    requests.get(url=url, headers=headers)
    plist = requests.get(url=url, headers=headers).json()
    return plist["name"]

def remove_playlist(access_token, uri):
    """
    unfollows one the user's playlist with the given URI
    :param access_token: securely determines the user
    :param uri: Idenifies the playlist to be deleted
    :return: Boolean of success
    """
    id = uri.split(":")[2]
    url = "https://api.spotify.com/v1/playlists/" + id + "/followers"
    headers = {"Authorization": "Bearer " + access_token}
    resp = requests.delete(url=url, headers=headers)
    return resp.status_code == 200

def get_tracks(access_token, uri):
    """
    gets the tracks from a user's playlist (public or private)
    :param access_token: securely ID's the user
    :return: returns a list of all track URI's
    """
    playlist_id = uri.split(":")[2]
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

def add_tracks_to_drain(access_token, drainlist, tracks):
    """
    Takes a list of tracks and a drainlist URI and appends the tracks to the drainlist
    :param access_token: Securely ID's User
    :param drainlist: drainlist sink URI
    :param tracks: list of track URI's to be added to the list
    :return:
    """
    track_list = split_list(tracks, 100)
    # if there are no tracks this is still an empty list, iterate through split list and upload
    id = drainlist.uri.split(":")[2]
    for tracks in track_list:
        trackstring = generate_uri_string(tracks)
        url = "https://api.spotify.com/v1/playlists/%s/tracks?uris=%s" % (id, trackstring)
        headers = {"Authorization": "Bearer " + access_token}
        requests.post(url=url, headers=headers)

def remove_tracks_from_drain(access_token, drainlist, tracks):
    """
    Takes a list of tracks and a drainlist URI and removes the tracks from the drainlist
    :param access_token: Securely ID's User
    :param drainlist: drainlist sink URI
    :param tracks: list of track URI's to be removed from the list
    :return:
    """
    id = drainlist.uri.split(":")[2]
    track_list = split_list(tracks, 100)
    for tracks in track_list:
        url = "https://api.spotify.com/v1/playlists/" + id + "/tracks"
        headers = {"Authorization": "Bearer " + access_token}

        data = {"tracks":[{"uri":track} for track in tracks]}
        requests.delete(url=url, headers=headers, json=data)
    else:
        return "no tracks"

####################################
###### End Spotify IO Code  ######## 
####################################


####################################
########### Utilities  #############
####################################


def split_list(tracks, splitsize):
    """
    Splits a list of tracks into sublists smaller than splitsize
    splitting is greedy, tracks are split into splitsize chunks
    until fewer than splitsize remain resulting in a smaller final sublist
    :param tracks: list of tracks URI's
    :param splitsize: max size of the returned sublists
    :return: list of lists of tracks
    """
    tracks =  list(tracks)
    end = splitsize
    ret = []
    front = 0
    while (front < len(tracks)):
        ret += [tracks[front:end]]
        front = end
        end = min(len(tracks), end + splitsize)
    return ret

def generate_uri_string(tracks):
    """
    changes a list of tracks into a properly formatted uri string for bulk loads
    :param tracks: list of tracks URI's
    :return: a formatted string to be used in HTTP requests
    """
    return "%2C".join(tracks)


####################################
###### Token Handling Code #########
####################################

##### User Interaction Token Code #####
# todo UI token code will be moved back to spotify.py or into another file
# backend Token code =/= frontend token code, for the backend if the tokens are hosed
# just give up and cry
def get_tokens_from_code(code):
    """
    Interim function, takes a "code" returned from the spotify auth API and acquires the users tokens
    :param code: auth string from Spotify API
    :return: POSTs the code and returns the response, containing the tokens
    """
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

def print_sources(sources):
    return [{"Name":s.name, "URI":s.uri} for s in sources]

####################################
######### End Utilities  ###########
####################################
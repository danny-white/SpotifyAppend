from flask import Flask, redirect, request
import urllib
import requests
import json 
import base64
import time
from playlist import *
import os

app = Flask(__name__)


# todo: change the API so that functions take in args for local testing, then create wrapper funcs that simply call the local 
# func after extracting the args from a request

# this needs to change at some point but not now
myUrl = "http://127.0.0.1:5000/"
# todo change this to return to the frontend homepage
auth_completed_url = myUrl + "authentication_completed"


sec = []
with open("Secrets", "r") as infile:
    for line in infile:
        sec.append(line.strip())
client_id = sec[0]
client_secret= sec[1]

# Get these The F out of here eventually
global access_token
global refresh_token 

####################################
###########  Auth Code  ############  
####################################
@app.route("/")
def initialize():
    if validate_tokens():
        return redirect(auth_completed_url)
    else:
        return get_new_tokens()

@app.route("/authentication_return")
def get_tokens():
    # upon successful authentication, we come here
    code = ""
    try: 
        code = request.args["code"]
    except:
         print("the code was not present, auth failed")
         redirect(myUrl)
    
    # if auth succeeds we build the url to get our tokens from the "code"
    response = get_tokens_from_code(code)

    # extract the tokens and save them 
    jsonResp = response.json()
    set_access_token(jsonResp["access_token"])
    set_refresh_token(jsonResp["refresh_token"])
    ttl = jsonResp["expires_in"]
    expires_at = int(time.time()) + ttl 
    
    # Save the Tokens back to the File, and redirect back to the complete page
    save_tokens(access_token, refresh_token, expires_at)
    return redirect(auth_completed_url)            

@app.route("/authentication_completed")
def signed_in():
    do_work("Danny", None)
    return "you made it"
####################################
######### End Auth Code  ########### 
####################################

####################################
######## Interactive Code ##########
####################################

@app.route("/list_drains")
def list_drains_request():
    resp = app.make_response(json.dumps({"this": "that", "These":"Those"}))
    return resp

def list_drains(user):
    return [filename for filename in os.listdir(os.getcwd()+ "/" + user + "/Playlists") if filename.endswith("_drain")]


@app.route("/new_drain")
def create_new_drain_request():
    print(request.args)
    ret = create_new_drain(request.args["drainlist"], request.args["sources"])
    return app.make_response(ret)
    # return proper JSON here

def create_new_drain(drainlist, sources):
    with open_playlist(drainlist + "_drain", "w+") as dfile:
        json.dump({"Playlist_URI": drainlist, "Sources": sources}, dfile)
    return json.dumps({"Playlist_URI": drainlist, "Sources": sources})

####################################
###### End Interactive Code ########
####################################


####################################
########### Sync Code  ############# 
####################################

def do_work(user, drainlist):
    # checks tokens updates if needed
    if not check_runtime_tokens():
        validate_tokens("Danny")
    # gets all the playlists in the sources, writes them out to disk
    for playlist in get_playlists():
        if playlist["name"] in ["Squaw", "Tycho"]:
            tracklist = get_tracks(playlist["id"])
            write_out_tracklist(user, playlist["name"], playlist["uri"],tracklist)
    
    # open the requisite drainlist
    dlist_name = "spotify:playlist:069rrIb9s1MRw2BBwXmeJE_drain"
    Dlist = 0 
    with open_playlist(dlist_name, "r") as out:
        Dlist = Drainlist(out)
    
    # run the sync program
    diff = Dlist.sync()
    # apply the diff to reference lists
    Dlist.write_out()
    # add them to the drain playlist
    add_tracks_to_drain(Dlist, diff)
    # cleanup the files 
    Dlist.cleanup(user)

# takes a downloaded plist (from spotify, not the playlist class), 
# writes it out, if a reference does not exist, create one that is the same as the tracklist
# if the reference does exist do not modify it
def write_out_tracklist(user, playlist_name, playlist_uri, tracklist):
    with open(user + "/Playlists/" + playlist_uri, "w+") as outfile:
        json.dump({"Playlist_URI":playlist_uri, "Track_URIs":tracklist}, outfile)
    try:
        open(user + "/Playlists/" + playlist_uri + "_ref", "r")
    except:
        with open(user + "/Playlists/" + playlist_uri + "_ref", "w+") as outfile:
            json.dump({"Playlist_URI":playlist_uri, "Track_URIs":tracklist}, outfile)

    
# get's a list of playlists for the current user
def get_playlists():
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + access_token}
    requests.get(url=url, headers=headers) 
    try:
        all_playlists = requests.get(url=url, headers=headers).json()
        return all_playlists["items"]
    except:
        print("unable to acquire playlist list")


# Takes a playlist id, (not URI) and returns the list of track uri's
def get_tracks(playlist_id):
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
def add_tracks_to_drain(drainlist, tracks):
    print(tracks)
    track_list = split_list(tracks, 100) 
    # if there are no tracks this is still an empty list, iterate through split list and upload
    for tracks in track_list:
        trackstring = generate_uri_string(tracks)
        url = "https://api.spotify.com/v1/playlists/%s/tracks?uris=%s" % (drainlist.name.split(":")[2], trackstring)
        headers = {"Authorization": "Bearer " + access_token}
        retVal = requests.post(url=url, headers=headers)
    else:
        return "no tracks"

# splits a list into sublists of len splitsize, last sublist may be smaller if not enough elements are present (no padding)
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

def generate_uri_string(tracks):
    return "%2C".join(tracks)

####################################
######### End Sync Code  ########### 
####################################



####################################
###### Token Handling Code ######### 
####################################

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
    return redirect(a.url)

def validate_tokens(user="Danny"):
    tokens = check_tokens(user)
    print(tokens)
    if tokens:
        set_access_token(tokens["access_token"])
        set_refresh_token(tokens["refresh_token"])
        if tokens["expires_at_epoch"] > int(time.time()) + 60 * 5:
            return tokens  
        else:
            access_token, ttl = refresh_tokens(user)
            set_access_token(access_token)
            expires_at = int(time.time()) + ttl 
            save_tokens(access_token, refresh_token, expires_at)
            return True
    else:
        print("Tokens are missing or corrupted")
        return None

def check_tokens(user):
    try:
        with tokenfile_open(user, "r+") as infile:
            return json.load(infile)
    except:
        return None
def check_runtime_tokens():
    global access_token, refresh_token
    try:
        return access_token and refresh_token
    except NameError:
        return 0

def refresh_tokens(user):
    url = "https://accounts.spotify.com/api/token/"
    data = {"grant_type" : "refresh_token", "refresh_token" : refresh_token}
    headers = make_authorization_headers(client_id, client_secret)
    resp = requests.post(url=url, data = data, headers = headers).json()
    return resp["access_token"], resp["expires_in"]

def save_tokens(access_token, refresh_token, expires_at, user="Danny"):
    dataOut = {"expires_at_epoch": expires_at, "access_token": access_token, "refresh_token": refresh_token}
    with tokenfile_open(user, "w") as outfile:
        json.dump(dataOut, outfile)

def tokenfile_open(user, flag):
    return open(user + "/" + user + "_tokens", flag)

def make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(str(client_id + ':' + client_secret).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

def set_access_token(new_access_token):
    global access_token
    access_token = new_access_token

def set_refresh_token(new_refresh_token):
    global refresh_token
    refresh_token = new_refresh_token

####################################
#### End Token Handling Code ####### 
####################################



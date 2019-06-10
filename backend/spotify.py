from flask import Flask, redirect, request
import urllib
import requests
import json 
import base64
import time
from playlist import *
import io
import os

####################################
######## Set up Constants ##########  
####################################

app = Flask(__name__)
cwd = "/Users/Danny/Documents/CS/SpotifyAppend/backend"

# hacky test global thing, will remove later once the frontend is properly attached 
user = "Danny" if __name__ == "__main__" else "Test_User" 

# todo: change the API so that functions take in args for local testing, 
# then create wrapper funcs that simply call the local 
# func after extracting the args from a request

# this needs to change at some point but not now
myUrl = "http://127.0.0.1:5000/"
# todo change this to return to the frontend homepage
auth_completed_url = myUrl + "authentication_completed"

sec = []
with open(cwd + "/Secrets", "r") as infile:
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

# This code is called when the app is first accessed from the Client, if the 
# Tokens are present it presents the landing page, if not it requests tokens
@app.route("/")
def initialize():
    if validate_tokens(user):
        return redirect(auth_completed_url)
    else:
        return get_new_tokens()

# Landing page to return from a Spotify Token Request
@app.route("/authentication_return")
def get_tokens():
    code = ""
    try: 
        code = request.args["code"]
    except:
         print("the code was not present, auth failed")
         redirect(myUrl)
    
    # if auth succeeds we build the url to get our tokens from the "code"
    response = get_tokens_from_code(code)

    # Save Tokens
    jsonResp = response.json()
    set_access_token(jsonResp["access_token"])
    set_refresh_token(jsonResp["refresh_token"])
    ttl = jsonResp["expires_in"]
    expires_at = int(time.time()) + ttl 
    
    save_tokens(access_token, refresh_token, expires_at, user)
    return redirect(auth_completed_url)            

# This is the "Main Page" that we will do our main work from 
# (managing drainlists).
# todo a one time refresh button to override the playlist refresh timer
@app.route("/authentication_completed")
def signed_in():
    return "you made it"
####################################
######### End Auth Code  ########### 
####################################

####################################
######## Interactive Code ##########
####################################

# Takes drains and formats them to be sent to the frontend
@app.route("/list_drains")
def list_drains_request():
    resp = app.make_response(json.dumps({"this": "that", "These":"Those"}))
    return resp

# Collects all drains associated with a user
def list_drains(user):
    return [filename for filename in os.listdir(os.getcwd()+ "/" + user + "/Playlists") if filename.endswith("_drain")]

# Takes new drainlist data and formats to be sent to frontend
@app.route("/new_drain")
def create_new_drain_request():
    ret = create_new_drain(request.args["drainlist"], request.args["sources"])
    return app.make_response(ret)
    # return proper JSON here

# creates a new drainlist
# args: drainlist = new name from drainlist (will overwrite old ones)
#       sources = list of playlist URI's 
def create_new_drain(user, drainlist, sources):
    if "spotify:playlist:" not in sources[0]:
        sources = ["spotify:playlist:" + source for source in sources]
    with open_playlist(user, drainlist, "w+") as dfile:
        json.dump({"Playlist_URI": drainlist, "Sources": sources}, dfile)
    return json.dumps({"Playlist_URI": drainlist, "Sources": sources})

####################################
###### End Interactive Code ########
####################################


# given a list of sources, download them, get your drainlist, and syncs everything
# this should be changed to take in a drainlist object
def do_work(user, source_names, dlist_name):
    # checks tokens updates if needed
    if not check_runtime_tokens():
        validate_tokens(user)
    # gets all the playlists in the sources, writes them out to disk
    for playlist in io.get_playlists(access_token):
        if playlist["id"] in source_names:
            tracklist = io.get_tracks(access_token, playlist["id"])
            write_out_tracklist(user, playlist["name"], playlist["uri"], tracklist)
    
    # open the requisite drainlist
    Dlist = 0 
    with open_playlist(user, dlist_name, "r") as out:
        Dlist = Drainlist(user, out)

    # run the sync program
    diff = Dlist.sync()
    # apply the diff to reference lists
    Dlist.write_out()
    # add them to the drain playlist
    io.add_tracks_to_drain(Dlist, diff)
    # cleanup the files 
    Dlist.cleanup(user)

# using the arguments, creates a saved version of the playlist, and 
# saves a new reference playlist. If a reference already exists, skip
# this does not user in memory playlist objects, just raw data from Spotify
# args: user = name of the current user
#       playlist_name = name of the playlist being written out
#       playlist_uri = spotify internal code for the playlist
#       tracklist = list of tracks corresponding to this playlist
def write_out_tracklist(user, playlist_name, playlist_uri, tracklist):
    with open(user + "/Playlists/" + playlist_uri, "w+") as outfile:
        json.dump({"Playlist_URI":playlist_uri, "Track_URIs":tracklist}, outfile)
    try:
        with open(user + "/Playlists/" + playlist_uri + "_ref", "r") as outfile:
            1
    except:
        with open(user + "/Playlists/" + playlist_uri + "_ref", "w+") as outfile:
            json.dump({"Playlist_URI":playlist_uri, "Track_URIs":tracklist}, outfile)




####################################
###### Token Handling Code ######### 
####################################
# PURE SPOTIFY API CALL
def get_tokens_from_code(code):
    url = "https://accounts.spotify.com/api/token/"
    params = {"grant_type" :"authorization_code", "code" : code, "redirect_uri":myUrl + "authentication_return"}
    headers = make_authorization_headers(client_id, client_secret) 
    return requests.post(url=url, data=params, headers=headers)

# Builds the Authentication URL and redirects the user there, so more tokens can be gathered
# PURE SPOTIFY API CALL
def get_new_tokens():
    url = "https://accounts.spotify.com/authorize/"
    scopes = "playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative user-follow-read"
    params = { "client_id":client_id, "response_type":"code", "redirect_uri": myUrl + "authentication_return", "scope":scopes}
    a = requests.get(url=url, params=params)
    return redirect(a.url)

def validate_tokens(user):
    tokens = check_tokens(user)
    if tokens:
        set_access_token(tokens["access_token"])
        set_refresh_token(tokens["refresh_token"])
        if tokens["expires_at_epoch"] > int(time.time()) + 60 * 5:
            return tokens  
        else:
            access_token, ttl = refresh_tokens(user)
            set_access_token(access_token)
            expires_at = int(time.time()) + ttl 
            save_tokens(access_token, refresh_token, expires_at, user)
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
# PURE SPOTIFY API CALL
def refresh_tokens(user):
    url = "https://accounts.spotify.com/api/token/"
    data = {"grant_type" : "refresh_token", "refresh_token" : refresh_token}
    headers = make_authorization_headers(client_id, client_secret)
    resp = requests.post(url=url, data = data, headers = headers).json()
    return resp["access_token"], resp["expires_in"]

def save_tokens(access_token, refresh_token, expires_at, user):
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
######### End Utilities  ###########
####################################

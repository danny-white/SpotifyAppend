from flask import Flask, redirect, request
import urllib
import requests
import json 
import base64
import time
import playlist, spio
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

# todo change this to return to the frontend homepage
auth_completed_url = spio.myUrl + "authentication_completed"

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
    try:
        spio.get_access_token(user)
        return redirect(auth_completed_url)
    except:
        return redirect(spio.get_new_tokens().url)

# Landing page to return from a Spotify Token Request
@app.route("/authentication_return")
def get_tokens():
    code = ""
    try: 
        code = request.args["code"]
    except:
         print("the code was not present, auth failed")
         redirect(spio.myUrl)
    
    # if auth succeeds we build the url to get our tokens from the "code"
    response = spio.get_tokens_from_code(code)

    # Save Tokens
    jsonResp = response.json()

    ttl = jsonResp["expires_in"]
    expires_at = int(time.time()) + ttl

    # todo unsure where the rest of the vars for the tokens are from, could be a simple jsonresp.dump

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
    with playlist.open_playlist(user, drainlist, "w+") as dfile:
        json.dump({"Playlist_URI": drainlist, "Sources": sources}, dfile)
    return json.dumps({"Playlist_URI": drainlist, "Sources": sources})

####################################
###### End Interactive Code ########
####################################


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







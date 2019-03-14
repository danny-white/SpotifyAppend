from flask import Flask, redirect, request
import urllib
import requests
import json 
import base64
import time

app = Flask(__name__)

# this needs to change at some point but not now
myUrl = "http://127.0.0.1:5000/"
sec = []
with open("Secrets", "r") as infile:
    for line in infile:
        sec.append(line.strip())
client_id = sec[0]
client_secret= sec[1]

# Get these The F out of here eventually
global access_token
global refresh_token 

# Should check the token file, if the token file is missing or corrupted then get new ones
# If the tokens are expired, use the refresh to get a new one
# otherweise use the access token 
@app.route("/")
def initialize():
    if validate_tokens():
        return redirect(myUrl + "login_completed")
    else:
        return get_new_tokens()

@app.route("/login_landing")
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
    return redirect(myUrl + "login_completed")            

@app.route("/login_completed")
def do_work():
    if not check_runtime_tokens():
        validate_tokens("Danny")
    all_playlists = get_playlists().json()
    for playlist in all_playlists["items"]:
        if playlist["name"] == "Squaw":
            tracklist = get_tracks(playlist["id"])
            write_out_tracklist("Danny", playlist["name"], playlist["uri"],tracklist)
    return "really really don"


def get_playlists():
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + access_token}
    return requests.get(url=url, headers=headers) 

# Takes a playlist id, not URI and returns the list of uri's
def get_tracks(playlist_id):
    url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
    headers = {"Authorization": "Bearer " + access_token}
    tracks = requests.get(url=url, headers=headers)
    jsonTrack = tracks.json()
    return [jsonTrack["items"][i]["track"]["uri"] for i in range(len(jsonTrack["items"]))]

def write_out_tracklist(user, playlist_name, playlist_uri, tracklist):
    with open(user + "/Playlist_" + playlist_name, "w+") as outfile:
        json.dump({"Playlist_URI":playlist_uri, "Track_URIs":tracklist}, outfile)



#########################
#  Token Handling Code  #
#########################

def get_tokens_from_code(code):
    url = "https://accounts.spotify.com/api/token/"
    params = {"grant_type" :"authorization_code", "code" : code, "redirect_uri":myUrl + "login_landing"}
    headers = make_authorization_headers(client_id, client_secret) 
    return requests.post(url=url, data=params, headers=headers)

# Builds the Authentication URL and redirects the user there, so more tokens can be gathered
def get_new_tokens():
    url = "https://accounts.spotify.com/authorize/"
    scopes = "playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative user-follow-read"
    params = { "client_id":client_id, "response_type":"code", "redirect_uri": myUrl + "login_landing", "scopes":scopes}
    a = requests.get(url=url, params=params)
    return redirect(a.url)

def validate_tokens(user="Danny"):
    tokens = check_tokens(user)
    if tokens:
        set_access_token(tokens["access_token"])
        set_refresh_token(tokens["refresh_token"])
        if tokens["expires_at_epoch"] > int(time.time()) + 60 * 5:
            return tokens  
        else:
            print("ere")
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
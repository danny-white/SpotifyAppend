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

print(client_id)
print(client_secret)
exit()

# Get these The F out of here eventually
global access_token
global refresh_token 


@app.route("/")
def initialize():
    if validate_tokens():
        return redirect(myUrl + "login_completed")
    else:
        # builds the Authentication URL and redirects the user there
        url = "https://accounts.spotify.com/authorize/"
        scopes = "playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative user-follow-read"
        params = { "client_id":client_id, "response_type":"code", "redirect_uri": myUrl + "login_landing", "scopes":scopes}
        a = requests.get(url=url, params=params)
        return redirect(a.url)

@app.route("/login_completed")
def do_work():
    all_playlists = get_playlists().json()
    for playlist in all_playlists["items"]:
        if playlist["name"] == "Tycho":
            tracklist = get_tracks(playlist["id"])
            print(tracklist)
    return "done"

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
    url = "https://accounts.spotify.com/api/token/"
    params = {"grant_type" :"authorization_code", "code" : code, "redirect_uri":myUrl + "login_landing"}
    headers = make_authorization_headers(client_id, client_secret) 
    r = requests.post(url=url, data=params, headers=headers)

    # extract the tokens and save them 
    jsonResp = r.json()
    access_token = jsonResp["access_token"]
    refresh_token = jsonResp["refresh_token"]
    ttl = jsonResp["expires_in"]
    expires_at = int(time.time()) + ttl 
    save_tokens(access_token, refresh_token, expires_at)
    validate_tokens()

    return redirect(myUrl + "login_completed")

def refresh(refresh_token):
    url = "https://accounts.spotify.com/api/token/"
    data = {"grant_type" : "refresh_token", "refresh_token" : refresh_token}
    headers = make_authorization_headers(client_id, client_secret)
    return requests.post(url=url, data = data, headers = headers)

def make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(str(client_id + ':' + client_secret).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

def save_tokens(access_token, refresh_token, expires_at, user="Danny"):
    dataOut = {"expires_at_epoch": expires_at, "access_token": access_token, "refresh_token": refresh_token}
    with tokenfile_open(user, "w") as outfile:
        json.dump(dataOut, outfile)

def check_tokens(user):
    try:
        with tokenfile_open(user, "r+") as infile:
            return json.load(infile)
    except:
        return None
            
def validate_tokens(user="Danny"):
    tokens = check_tokens(user)
    if tokens:
        global access_token, refresh_token
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        return tokens["expires_at_epoch"] > int(time.time()) + 60 * 5
    else:
        print("Tokens have expired")
        return None

def get_playlists():
    global access_token
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + access_token}
    return requests.get(url=url, headers=headers) 

# Takes a playlist id, not URI and returns the list of uri's
def get_tracks(playlist_id):
    global access_token
    url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
    headers = {"Authorization": "Bearer " + access_token}
    tracks = requests.get(url=url, headers=headers)
    jsonTrack = tracks.json()
    return [jsonTrack["items"][i]["track"]["uri"] for i in range(len(jsonTrack["items"]))]

def tokenfile_open(user, flag):
    return open(user + "/" + user + "_tokens", flag)
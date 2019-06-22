from flask import Flask, redirect, request
import urllib
import requests
import json 
import base64
import time
import playlist, spio
import io
import os
from flask_cors import CORS


####################################
######## Set up Constants ##########  
####################################

app = Flask(__name__)
CORS(app)
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

# Takes playlists owned by the user and formats them to be sent to the frontend
@app.route("/list_playlists")
def list_playlists_request():
    user = request.args["user"]
    lists = spio.get_playlists(spio.get_access_token(user))
    resp = app.make_response(json.dumps([{"name": l["name"], "uri": l["uri"]} for l in lists]))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/list_drains")
def list_drains_request():
    user = request.args["user"]

    drain_names = [f for f in os.listdir(user + "/Playlists/") if f.endswith("_drain")]

    drains = []
    for d in [d.strip("_drain") for d in drain_names]:
        with playlist.open_drainlist(user, d) as infile:
            drains.append(playlist.Drainlist(user, infile))
    resp = app.make_response(json.dumps([{"Name": d.name, "URI": d.uri, "Sources": spio.print_sources(d.sources)} for d in drains]))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# Collects all drains associated with a user
def list_drains(user):
    return [filename for filename in os.listdir(os.getcwd()+ "/" + user + "/Playlists") if filename.endswith("_drain")]

@app.route("/refresh")
def refresh_request():
    user = request.args["user"]
    token = spio.get_access_token(user)
    refresh(user, token)
    resp = app.make_response("success")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Takes new drainlist data, generates the proper drainlist (creating a playlist to serve as the sink)
@app.route("/new_drain", methods = ["GET", "POST", "OPTIONS"])
def create_new_drain_request():
    if request.method == "OPTIONS":
        resp = app.make_response(json.dumps([{"name":"nope"}]))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers["Access-Control-Allow-Headers"] = "*"
        return resp
    if request.method == "POST":
        data = request.data.decode("utf-8")
        data = json.loads(data)
        ret = create_new_drain_from_name(data["user"] ,data["drainlist"], data["sources"])
        return app.make_response(ret)
    # return proper JSON here

def create_new_drain_from_name(user, dlistName, sources):
    """
    Given a name (non-URI) this creates a new sink playlist and sets up the URI work as expected
    :param user: User owning the Drainlist
    :param dlistName: name for the sink playlist (Spotify Name)
    :param sources: sources to be associated with the new Drainlist
    :return:
    todo prevent name collisions
    """
    # create new playlist with given name, get the URI and proceed
    uri = spio.create_playlists(spio.get_access_token(user), dlistName)
    return create_new_drain(user, dlistName, uri, sources)

def create_new_drain(user, dListNameame,  drainlist, sources):
    """
    Creates a new drainlist
    :param user: User owning the Drainlist
    :param drainlist: Name for new Drainlist (should be a URI)
    :param sources: list of sources to associate with the new drain
    :return: the contents of the file as a string
    """
    if "spotify:playlist:" not in sources[0]:
        sources = ["spotify:playlist:" + source for source in sources]
    sources = [{"URI": source, "Name":spio.get_name(spio.get_access_token(user), source)} for source in sources]
    with playlist.open_drainlist(user, drainlist, "w+") as dfile:
        json.dump({"Name": dListNameame,"Playlist_URI": drainlist, "Sources": sources}, dfile)

    with playlist.open_drainlist(user, drainlist) as dfile:
        dlist = playlist.Drainlist(user, dfile)

    dlist.populate(spio.get_access_token(user))
    dlist.cleanup(user)

    return json.dumps({"Name": dListNameame,"Playlist_URI": drainlist, "Sources": sources})

####################################
###### End Interactive Code ########
####################################

def refresh(user, token):
    """
    Refreshes / updates all of a users drainlists
    The grandaddy of them all
    :param user: The user who we are updating
    :param token: The users token
    :return: None
    """
    uris = [f for f in os.listdir(user + "/Playlists/") if "_ref" not in f]
    print(uris)
    for uri in uris:
        with playlist.open_drainlist(user, uri) as infile:
            d = playlist.Drainlist(user, infile)

        diff = d.sync()
        d.write_out()
        spio.add_tracks_to_drain(token, d, diff)
        d.cleanup(user)


# user = "Danny"
# token = spio.get_access_token(user)
# u = ["spotify:playlist:16wE0quJ4wHXGaY78MZikr", "spotify:playlist:0FMPIrKYN6hIEH54FyZ1oa"]

# refresh(user, token)




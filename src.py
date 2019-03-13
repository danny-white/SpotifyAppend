from flask import Flask, redirect, request
import urllib
import requests
import json 
import base64
import time

app = Flask(__name__)
myUrl = "http://127.0.0.1:5000/"
client_id ='7a1454711b0e4883affd973ca35a67e2'
client_secret= '3c6e13176b624a84b44aab94a5c1df9b'

global access_token
global refresh_token 
# params is query string
# data is body

@app.route("/")
def initialize():
    if validate_tokens():
        return redirect(myUrl + "login_completed")
    else:
        # builds the Authentication URL and redirects the user there
        url = "https://accounts.spotify.com/authorize/"
        params = { "client_id":client_id, "response_type":"code", "redirect_uri": myUrl + "login_landing" }
        a = requests.get(url=url, params=params)
        return redirect(a.url)

@app.route("/login_completed")
def do_work():
    global access_token, refresh_token
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": "Bearer " + access_token, "Accept": "application/json", "Content-Type": "application/json"}
    r = requests.get(url=url, headers=headers) 
    print(r.text)
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

    return "tokens saved"

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
    with open(user + "_tokens", "w") as outfile:
        json.dump(dataOut, outfile)

def check_tokens(user):
    try:
        with open(user + "_tokens", "r+") as infile:
            return json.load(infile)
    except:
        return None
            
def validate_tokens(user="Danny"):
    tokens = check_tokens(user)
    if tokens:
        global access_token, refresh_token
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print("saved")
        return tokens["expires_at_epoch"] > int(time.time()) + 60 * 5
    else:
        print("Tokens have expired")
        return None






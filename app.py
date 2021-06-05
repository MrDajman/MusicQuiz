from math import e
import requests
import json
from flask import Flask, render_template, request, session, url_for, current_app, redirect, flash, Response, send_from_directory
import random
#import string

app = Flask(__name__)
app.secret_key = "hello"

@app.route('/')
def home():
    #base_url = "https://api.deezer.com/track/"
    #track_id = 1173900882
    #r = requests.get(base_url+str(track_id))
    #preview_url = r.json()["preview"]
    #print(preview_url)
    
    #r = requests.get(preview_url)

    #with open('static/song.mp3', 'wb') as f:
    #    f.write(r.content)

    return render_template("home.html")
    #return render_template("base.html", preview_local_url = "downloads/song.mp3")



@app.route('/artist_info', methods=['POST'])
def artist_info():
    artist_name = request.form['artistName']

    print(artist_name)
    song_list = get_artist_song_list(str(artist_name))

    session['song_list'] = song_list
    session['artist_name'] = artist_name
    session["current_song"] = ""
    print(song_list)
    #download_random_song(song_list)
    return render_template("artist_info.html", artist_name = artist_name, found_songs = len(song_list))



@app.route('/game', methods=['GET', 'POST'])
def game():
    
    
    prev_song = session["current_song"]
    print(prev_song)
    if request.method == "POST":
        answer = request.form['answer']
        #print(answer)
        #print(session["current_song"])
        if answer.lower() == session["current_song"].lower():
            good_answer = 1
        else:
            good_answer = 0
    else:
        good_answer = 2

    
    session["current_song"] = get_random_song(session['song_list'])
    #print("xx")
    #print(session["current_song"])
    song_mp3_url = get_random_song_mp3(session['current_song'],session['artist_name'])
    
    #send_from_directory("static", "static/")
    return render_template("music_game.html", 
                            artist_name = session['artist_name'], 
                            song_url = song_mp3_url, 
                            good_answer = good_answer,
                            prev_song_title = prev_song)

def get_artist_song_list(artist_name):
    song_title_list = []
    # get artist id
    
    base_url = "https://www.theaudiodb.com/api/v1/json/1/search.php?s="
    r = requests.get(base_url+str(artist_name))
    #print(r)
    print(r.json()["artists"][0]["idArtist"])
    artist_id = r.json()["artists"][0]["idArtist"]

    # get discography
    base_url = "https://theaudiodb.com/api/v1/json/1/album.php?i="
    r = requests.get(base_url+str(artist_id))

    for album in (r.json()["album"]):
        #print(album["idAlbum"])
        album_id = album["idAlbum"]
        
        # get songs
        base_url = "https://theaudiodb.com/api/v1/json/1/track.php?m="
        r = requests.get(base_url+str(album_id))
        for track in r.json()["track"]:
            #print(track["strTrack"])
            song_title_list.append(track["strTrack"])
    
    return song_title_list

def get_random_song(song_title_list):
    random_song = random.choice(song_title_list)
    print(random_song)
    return random_song

def download_random_song(random_song, artist_name):

    print(random_song)
    base_url = "https://api.deezer.com/search?q="
    r = requests.get(base_url+str(random_song+" "+artist_name))
    #print(r.json())
    preview_url = r.json()["data"][0]["preview"]
    print(r.json()["data"][0]["preview"])
    print(r.json()["data"][0]["title"])
    print(preview_url)
    r = requests.get(preview_url)

    with open('static/song.mp3', 'wb') as f:
        f.write(r.content)

    #return song_title_list

def get_random_song_mp3(random_song, artist_name):

    #random_song = random.choice(song_title_list)
    print(random_song)

    
    base_url = "https://api.deezer.com/search?q="
    complete_url = base_url+str(random_song+" "+artist_name)
    print(complete_url)
    r = requests.get(complete_url)
    #print(r.json())
    preview_url = r.json()["data"][0]["preview"]

    return preview_url


if __name__ == '__main__':
    #download_random_song(artist_name = "Dawid Podsiadło")
    app.run(debug=True)
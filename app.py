import requests
import json
from flask import Flask, render_template, request, session, url_for, current_app, redirect, flash, Response
import random

app = Flask(__name__)
app.secret_key = "hello"

@app.route('/')
def home():
    base_url = "https://api.deezer.com/track/"
    track_id = 1173900882
    r = requests.get(base_url+str(track_id))
    preview_url = r.json()["preview"]
    #print(preview_url)
    
    r = requests.get(preview_url)

    with open('static/song.mp3', 'wb') as f:
        f.write(r.content)

    return render_template("base.html", preview_local_url = "downloads/song.mp3")

def download_random_song(artist_name):
    song_title_list = []
    # get artist id
    
    base_url = "https://www.theaudiodb.com/api/v1/json/1/search.php?s="
    r = requests.get(base_url+str(artist_name))
    #print(r)
    #print(r.json()["artists"][0]["idArtist"])
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
    
    random_song = random.choice(song_title_list)
    print(random_song)

    
    base_url = "https://api.deezer.com/search?q="
    r = requests.get(base_url+str(random_song+" "+artist_name))
    #print(r.json())
    preview_url = r.json()["data"][0]["preview"]
    print(r.json()["data"][0]["preview"])
    print(r.json()["data"][0]["title"])

    r = requests.get(preview_url)

    with open('static/song.mp3', 'wb') as f:
        f.write(r.content)

    #return song_title_list


if __name__ == '__main__':
    download_random_song(artist_name = "Dawid Podsiadło")
    #app.run(debug=True)
import requests
from flask import Flask, render_template, request, session
import random
import re
from difflib import SequenceMatcher


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

    artist_found = 1
    song_list = get_artist_song_list(str(artist_name))
    song_list = list(set(song_list))
    if len(song_list) == 0:
        artist_found = 0
    session['song_list'] = song_list
    session['artist_name'] = artist_name
    session["current_song"] = ""
    session["total_points"] = 0
    session["songs_guessed"] = 0
    #download_random_song(song_list)
    return render_template("artist_info.html", artist_name = artist_name, found_songs = len(song_list), artist_found = artist_found)



@app.route('/game', methods=['GET', 'POST'])
def game():
    
    points = 0
    prev_song = session["current_song"]
    if request.method == "POST":
        session["songs_guessed"]+=1
        answer = request.form['answer']
        time_left = request.form['points']
        no_par = session["current_song"].lower()
        no_par = re.sub("\s?\(.*\)","",no_par)
        possible_answers = [session["current_song"].lower(), no_par]
        if answer == "                              ":
            good_answer = -1
            points = 0
        else:
            if answer.lower() in possible_answers:
                good_answer = 1
                points = (float(time_left)/30.0)*500 + 500 #time max -> 1000 pts; time 0 -> 500 pts
            else:
                sim = similar(answer.lower(), no_par)
                if sim> 0.6:
                    good_answer = 3
                    points = ((float(time_left)/30.0)*500 + 500) * 0.75 #time max -> 750 pts; time 0 ->  pts
                else:
                    good_answer = 0
                    points = 0
        if session["songs_guessed"] >= 10:
            return render_template("result.html", 
                            artist_name = session['artist_name'], 
                            good_answer = good_answer,
                            prev_song_title = prev_song,
                            total_points = session["total_points"],
                            last_points = points)
        
    else:
        good_answer = 2 # no post method -> print nothing

    points = int(points)
    session["total_points"] += points
    
    for i in range(10):
        session["current_song"],session['song_list']  = pop_random_song(session['song_list'])
        song_mp3_url = get_random_song_mp3(session['current_song'],session['artist_name'])
        if song_mp3_url != "not available":
            break
    
    if song_mp3_url == "not available":
        return "no music files available"

    #send_from_directory("static", "static/")
    return render_template("music_game.html", 
                            artist_name = session['artist_name'], 
                            song_url = song_mp3_url, 
                            good_answer = good_answer,
                            prev_song_title = prev_song,
                            total_points = session["total_points"],
                            last_points = points)

def get_artist_song_list(artist_name):
    song_title_list = []
    # get artist id
    
    base_url = "https://www.theaudiodb.com/api/v1/json/1/search.php?s="
    r = requests.get(base_url+str(artist_name))
    #print(r)
    try:
        if r.json()["artists"][0]["idArtist"] == None:
            return []
    except TypeError:
        return []
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
            if len(song_title_list) > 300:
                break
        if len(song_title_list) > 300:
            break
    
    return song_title_list

def pop_random_song(song_title_list):
    #random_song = random.choice(song_title_list)
    #print(random_song)
    random.shuffle(song_title_list)
    random_song = song_title_list[-1]
    song_title_list = song_title_list[:-1]
    #random_song = song_title_list.pop(random.randrange(len(song_title_list)))
    #print(random_song)
    return random_song,song_title_list 

def download_random_song(random_song, artist_name):

    base_url = "https://api.deezer.com/search?q="
    r = requests.get(base_url+str(random_song+" "+artist_name))
    #print(r.json())
    preview_url = r.json()["data"][0]["preview"]
    r = requests.get(preview_url)
    with open('static/song.mp3', 'wb') as f:
        f.write(r.content)

    #return song_title_list

def get_random_song_mp3(random_song, artist_name):

    #random_song = random.choice(song_title_list)
    print(random_song)

    
    base_url = "https://api.deezer.com/search?q="
    complete_url = base_url+str(random_song+" "+artist_name)
    #print(complete_url)
    r = requests.get(complete_url)
    #print(r.json())
    try:
        preview_url = r.json()["data"][0]["preview"]
        return preview_url
    except:
        print("PREVIEW NOT AVAILABLE!")
        return "not available"

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

if __name__ == '__main__':
    #download_random_song(artist_name = "Dawid Podsiadło")
    app.run(debug=True)
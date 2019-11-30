from flask import Flask, render_template, request, flash, redirect, session, jsonify
import requests
from jinja2 import StrictUndefined
from model import connect_db, db, Song, User, Annotation, seed_data
import genius

from bs4 import BeautifulSoup
import requests
# to access api key
import os


app = Flask(__name__)
app.secret_key = 'yliwmhd'

app.jinja_env.undefined = StrictUndefined

GENIUS_TOKEN = os.environ.get('TOKEN')
# GENIUS_URL = "http://104.17.212.67/"
GENIUS_URL = "https://api.genius.com/"


@app.route("/")
def homepage():

    # if not session.get('current_user'):
    #     return redirect("/user-reg")

    return render_template("react.html")

@app.route("/react")
def react():

    return render_template("react.html")

# @app.route("/results")
# def results():

#     search = request.args.get('q') # 'q' from index.html form input

#     payload = {'access_token' : GENIUS_TOKEN,
#                 'q': search}
#     url = GENIUS_URL + "search"
#     # print(url)
#     response = requests.get(url, params=payload)

#     # print(response.content)
#     data = response.json()

#     # go to search api > songs api > youtube video
#     song_title = data['response']['hits'][0]['result']['title']
#     artist = data['response']['hits'][0]['result']['primary_artist']['name']
#     lyrics_url = data['response']['hits'][0]['result']['url']
#     session['song_title'] = song_title
#     session['song_artist'] = artist

#     api_song = data['response']['hits'][0]['result']['api_path']

#     payload_song = {'access_token : GENIUS_TOKEN'}
#     url_song = GENIUS_URL + api_song.lstrip('/') # get rid of second slash
#     response_song = requests.get(url_song, params=payload)
#     data_song = response_song.json()

#     # video_url = data_song['response']['song']['media'][0]['url']
#     # session['video_url'] = video_url

#     media_list = data_song['response']['song']['media']
#     for idx, media in enumerate(media_list):
#         if media['provider']=="youtube":
#             session['video_url'] = media_list[idx]['url']
#             video_url = session['video_url'].replace("http://www.youtube.com/watch?v=","")

#     # web scraping
#     page = requests.get(lyrics_url)
#     # make Beautiful Soup elements from DOM
#     soup = BeautifulSoup(page.text, 'html.parser')
#     # from the webpage, get back the html element with the 'lyrics' class
#     lyrics = soup.find(class_='lyrics')
#     # lyrics as string with \n
#     lyrics_str = lyrics.get_text()
#     # replaced python's \n to html <br>, still in quotes
#     lyrics_html = lyrics_str.replace('\n','<br>')
#     session['lyrics'] = lyrics_html

#     # query any annotations for song searched
#     q_annotations = Annotation.query.filter(Song.song_title==session['song_title'],
#                                             Song.song_artist==session['song_artist']).join(Song).all()

#     return render_template("results.html", 
#                             song_title=song_title,
#                             artist=artist,
#                             lyrics_html=lyrics_html,
#                             video_url=video_url,
#                             q_annotations=q_annotations)

@app.route("/api/search")
def api_search():

    search = request.args.get('q')
    # a dictionary of api data
    search_dict = genius.search(search)

    # query for annotations of searched songs already in database
    q_annotations = db.session.query(Annotation.anno_id, Annotation.song_fragment, 
                                    Annotation.annotation).filter(Song.song_title==search_dict['song_title'],
                                    Song.song_artist==search_dict['song_artist']).join(Song).all()
    # print(q_annotations)
    # test
    # q_annotations = [['list1', 'list1-2'], ['list2', 'list2-2']]

    # add a key-value pair for the search list
    song_annos = []
    if q_annotations:
        for annotation in q_annotations:
            song_annos.append({'anno_id': annotation[0], 
            'song_fragment': annotation[1],
            'annotation': annotation[2]
            })

    search_dict['song_annos'] = song_annos

    return jsonify(search_dict)

@app.route("/json/allsongs")
def songs():

    allsongs = {'results': []}
    songs = db.session.query(Song.song_title, Song.song_artist).all()
    # print(songs)
    if songs:
        for song_tuple in songs:
            allsongs['results'].append({
                                'song_title': song_tuple[0],
                                'song_artist': song_tuple[1]
                                })

    return jsonify(allsongs)


@app.route("/user-reg")
def user():

    return render_template("/user.html")

@app.route("/user", methods=['POST'])
def user_session():

    name = request.form["name"]
    email = request.form["email"]

    new_user = User(email=email, name=name)
    db.session.add(new_user)
    db.session.commit()

    # made session the user_id since the User object by itself cannot be sessioned
    session['current_user'] = new_user.user_id
    print(session['current_user'])

    return redirect("/")

@app.route("/save", methods=['POST'])
def save():
    """Testing get user input and save to database"""

    annotation = request.form["annotation"]
    fragment = request.form["fragment"]
    song_title = request.form["song_title"]
    song_artist = request.form["song_artist"]
    lyrics = request.form["lyrics"]
    video_url = request.form["video_url"]

    new_annotation = Annotation(annotation=annotation, 
                                song_fragment=fragment)

    # need to query song from db to not duplicate
    q_song = Song.query.filter(Song.song_title==song_title,
                                Song.song_artist==song_artist).first()
    print(q_song)
    if q_song:
        new_song = q_song
    else:
        new_song = Song(song_title=song_title,
                        song_artist=song_artist,
                        lyrics=lyrics,
                        video_url=video_url)

    q = User.query.get(session['current_user'])
    q.annotations.append(new_annotation)
    new_song.annotations.append(new_annotation)

    db.session.add(new_song)
    db.session.add(new_annotation)
    db.session.commit()

    return redirect("/user-annos")

@app.route("/user-annos")
def user_annos():

    if session.get('current_user'):
        user = User.query.get(session['current_user'])
        annotations = user.annotations
        return render_template("user_annotations.html",
                                user=user,
                                annotations=annotations)
    else:
        flash('Please sign-in')
        return redirect('/user-reg')

# @app.route("/json/user-annos")
# def user_annos():

#     if session.get('current_user'):
#         user = User.query.get(session['current_user'])
#         annotations = user.annotations
#         return render_template("user_annotations.html",
#                                 user=user,
#                                 annotations=annotations)
#     else:
#         flash('Please sign-in')
#         return redirect('/user-reg')

# @app.route("/songs")
# def songs():

#     songs = Song.query.all()
#     return render_template("songs.html",
#                             songs = songs)

# @app.route("/songs/<int:song_id>")
# def song(song_id):

#     song = Song.query.get(song_id)
#     return render_template("song.html",
#                             song=song)

if __name__ == "__main__":
    connect_db(app)
    db.create_all()
    
    app.run(host="0.0.0.0", debug=True)
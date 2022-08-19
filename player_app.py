from flask import Flask, render_template, request
import spotipy
import spotipy.util as util
from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import DataRequired, Regexp
import threading
import sched
import time

# Auth for spotify
scope = "user-read-playback-state,user-modify-playback-state"
username = input("Username: ")

# Make sure to set environment variables for client id/secret and uri
token = util.prompt_for_user_token(username, scope)
sp = spotipy.Spotify(auth=token)

# Initialize scheduler
s = sched.scheduler(time.time, time.sleep)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

class MyForm(FlaskForm):
    mins = StringField(
        label="Enter minutes:", 
        validators=[Regexp(r'[1-9]+', message=("Must be only numbers (at least one)"))])


@app.route('/', methods=["GET", "POST"])
def index():
    form = MyForm()
    data = {}

    if form.validate_on_submit(): 
        delayMin = int(request.form['mins'])
        pause_after(delayMin)
        data.setdefault("delay", delayMin)


    if sp.current_user_playing_track():
        data.update({"title": sp.current_user_playing_track()['item']['name'],
                "artist": sp.current_user_playing_track()['item']['artists'][0]['name'],
                "device": sp.devices()['devices'][0]['name'],
                "img_url": sp.current_user_playing_track()['item']['album']['images'][1]['url']})
    else:
        data.update({"title": None,
                "artist": None,
                "device": None,
                "img_url": None})
    return render_template("index.html", **data, form=form)


def pause_after(mins):
    print(f"Timer set for {mins} minutes. Have a good rest!")
    s.enter(mins * 60, priority=1, action=sp.pause_playback)
    pauseThread = threading.Thread(target=s.run)
    pauseThread.start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

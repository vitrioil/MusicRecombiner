import json
import uuid
from pathlib import Path
from pprint import pprint

import numpy as np
import soundfile as sf

from werkzeug.utils import secure_filename

from flask import (render_template, request, jsonify,
                   send_from_directory)
from flask import Blueprint, session, redirect, url_for

# package import
from separator import Config, db
from separator.main.augment import Augment
from separator.models import Session, Music
from separator.main import gen_session, gen_music, gen_storage
from separator.main import UploadForm, AugmentForm, AugmentSignalForm
from separator.main import (save_audio, save_audio_from_storage,
                            store_combined_signal, split_or_load_signal)

main = Blueprint(name="main", import_name=__name__)

def _load_session(music_id, stem):
    get_data = lambda x, s: {"music_id": x, "music_name": Path(Music.query.get(x).file_path).name,
                             "stem": s}
    return [get_data(m, stem) for m in music_id]

@main.route('/', methods=["GET", "POST"])
def home():
    form = UploadForm()

    if session.get("session_id") is None:
        parent_dir = Path(main.root_path, Config.AUDIO_PATH)
        gen_session(session, parent_dir)

    if form.validate_on_submit():

        audio_file = request.files.get("audio")
        stem = form.stems.data
        session["stem"] = stem
        gen_music(session, audio_file)

        return redirect(url_for("main.augment"))

    previous_session = None
    if session.get("music_id") is not None:
        # get stuff
        music_id = session["music_id"]
        stem = session["stem"]
        previous_session = _load_session(music_id, stem)
    return render_template("home.html", form=form, title="Home",
                           previous_session=previous_session)

@main.route("/augment", methods=["GET"])
def augment():
    music_id = request.args.get("music_id")
    stem = request.args.get("stem", session["stem"])
    session_id = session["session_id"]

    if music_id is not None:
        music = Music.query.get_or_404(music_id)
    else:
        music = Music.query.get_or_404(session["music_id"])
    #after getting music, get file path
    file_path = music.file_path
    #now split or load
    names, dir_name, new_split = split_or_load_signal(file_path, stem, session_id,
                                                      session)

    return render_template("augment.html", title="Augment",
                           names=names, dir=dir_name,
                           augment=AugmentSignalForm().augment,
                           new_split=new_split)

@main.route("/augmented", methods=["POST"])
def augmented():
    music_id = session["music_id"][0]
    session_id = session["session_id"]
    signal = session.get("signal_augmented", session["signal"])

    json_data = request.get_json()
    signal= gen_storage(session, session_id, music_id, json_data, Augment(), signal)

    session["signal_augmented"] = signal
    store_combined_signal(signal, session["dir"], session["audio_meta"])
    return {"augmentation": "success"}

@main.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@main.route("/main/data/<path:subpath>")
def get_audio(subpath):
    return send_from_directory("main/data", subpath, mimetype="audio/mpeg",
                               attachment_filename=Path(subpath).name,
                               as_attachment=True)

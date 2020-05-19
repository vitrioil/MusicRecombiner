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
from separator.main import (UploadForm, AugmentForm, AugmentSignalForm,
                           Signal)
from separator.main import (save_audio, save_audio_from_storage,
                            store_combined_signal, split_or_load_signal,
                            undo_music)

main = Blueprint(name="main", import_name=__name__)

def _load_session(music_id, stems):
    get_data = lambda x, s: {"music_id": x, "music_name": Path(Music.query.get(x).file_path).name,
                             "stem": s}
    return [get_data(m, s) for m, s in zip(music_id, stems)]

@main.route('/', methods=["GET", "POST"])
def home():
    form = UploadForm()

    if session.get("session_id") is None:
        parent_dir = Path(main.root_path, Config.AUDIO_PATH)
        gen_session(session, parent_dir)

    if form.validate_on_submit():

        audio_file = request.files.get("audio")
        stem = form.stems.data
        gen_music(session, audio_file, stem)

        return redirect(url_for("main.augment"))

    previous_session = None
    if session.get("music_id") is not None:
        # get stuff
        music_id = session["music_id"]
        stems = [Music.query.get(m_id).stem for m_id in music_id]
        previous_session = _load_session(music_id, stems)
    return render_template("home.html", form=form, title="Home",
                           previous_session=previous_session)

@main.route("/augment", methods=["GET"])
def augment():
    music_id = request.args.get("musicID")
    session_id = session["session_id"]

    if music_id is not None:
        music = Music.query.get_or_404(music_id)
    else:
        # get the latest added music
        music_id = session["music_id"][-1]
        music = Music.query.get_or_404(music_id)

    stem = request.args.get("stem", music.stem)
    #after getting music, get file path
    file_path = music.file_path
    #now split or load
    print(music)
    names, dir_name, new_split = split_or_load_signal(file_path, stem, session_id,
                                                      session)
    # inform which music file to load
    file_path = Path(file_path)
    file_stem = file_path.stem
    print(file_path.parent)

    music_path = file_path.parent / file_stem
    # inform whether to load original or augmented audio
    count_stems = len(list((music_path / "original").rglob("*mp3")))
    count_augmented_stems = len(list((music_path / "augmented").rglob("*mp3")))
    load_augment = False
    if count_augmented_stems == count_stems:
        load_augment = True

    return render_template("augment.html", title="Augment",
                           names=names, dir=dir_name,
                           augment=AugmentSignalForm().augment,
                           load_augment=load_augment, file_stem=file_stem,
                           music_id=music_id)

@main.route("/augmented", methods=["POST"])
def augmented():
    music_id = request.args.get("musicID")
    music = Music.query.get_or_404(music_id)
    session_id = session["session_id"]

    file_path = Path(music.file_path)
    file_stem = file_path.stem
    sr = music.sample_rate
    signal = Signal.load_from_path(file_path.parent / file_stem / "augmented",
                                   file_path.parent / file_stem / "original",
                                   sr=sr)

    json_data = request.get_json()
    signal= gen_storage(session, session_id, music_id, json_data, Augment(), signal)

    store_combined_signal(signal, session["dir"], session["audio_meta"])
    return {"augmentation": "success"}

@main.route("/undo", methods=["POST"])
def undo():
    json_data = request.get_json()
    music_id = json_data["musicID"]
    stem_name = json_data["stemName"]
    undo_music(music_id, stem_name, session, Augment())
    return {"undo": "success"}

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

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
from separator import Config
from separator.main.augment import Augment
from separator.main.separate import SpleeterSeparator
from separator.main import UploadForm, AugmentForm, AugmentSignalForm
from separator.main import (save_audio, save_audio_from_storage, augment_data,
                            store_combined_signal)

main = Blueprint(name="main", import_name=__name__)

def load_separator(separator_name: str, *args, **kwargs):

    if separator_name.lower() == "spleeter":
        separator = SpleeterSeparator(*args, **kwargs)

    return separator

@main.route('/', methods=["GET", "POST"])
def home():
    form = UploadForm()
    if form.validate_on_submit():
        parent_dir = Path(main.root_path, Config.AUDIO_PATH)
        parent_dir.mkdir(exist_ok=True)
        session["dir"] = parent_dir / str(uuid.uuid4())

        audio_file = request.files.get("audio")
        audio_path, audio_meta = save_audio_from_storage(audio_file, session["dir"])

        session["audio_path"] = audio_path
        session["audio_meta"] = audio_meta
        session["stem"] = form.stems.data

        return redirect(url_for("main.augment"))
    return render_template("home.html", form=form, title="Home")

def _save_all(signal, augmented=False):
    augment_str = "augmented" if augmented else ''
    for name, sig in signal.get_items():
        signal_path = session["dir"] / augment_str / name
        save_audio(sig, signal_path, session["audio_meta"])

@main.route("/augment", methods=["GET"])
def augment():

    if request.method == "GET":
        if session.get("signal") is None:
            audio_path = session.get("audio_path")
            #separator = load_separator("spleeter", stems=session.get("stem", 2))
            #signal = separator.separate(audio_path.as_posix())
            import pickle
            with open("signal.pkl", 'rb') as f:
                signal = pickle.load(f)
            session["signal"] = signal
            _save_all(signal)

        signal = session.get("signal")
        names = signal.get_names()

    return render_template("augment.html", title="Augment",
                           names=names, dir=f"/main/data/{session['dir'].stem}",
                           augment=AugmentSignalForm().augment)

@main.route("/augmented", methods=["POST"])
def augmented():
    json_data = request.get_json()

    print(session.get("signal_augmented"), " augmented signal")
    signal = session.get("signal_augmented", session["signal"])
    signal = augment_data(Augment(), signal, json_data, session["audio_meta"])

    _save_all(signal, augmented=True)
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

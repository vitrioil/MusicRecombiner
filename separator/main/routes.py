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
from separator.main import save_audio, save_audio_from_storage, augment_data

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

@main.route("/augment", methods=["GET", "POST"])
def augment():
    def _save_all(signal, augmented=False):
        augment_str = "_augmented" if augmented else ''
        for name, sig in signal.get_items():
            signal_path = session["dir"] / (name + augment_str)
            save_audio(sig, signal_path, session["audio_meta"])

    load_augment = json.loads(request.args.get("augment", 'true').lower())

    if request.method == "POST":
        json_data = request.get_json()

        print(session.get("signal_augmented"), " augmented signal")
        signal = session.get("signal_augmented", session["signal"])
        signal = augment_data(Augment(), signal, json_data, session["audio_meta"])

        _save_all(signal, augmented=True)
        session["signal_augmented"] = signal
        return redirect(url_for("main.augment"))

    elif request.method == "GET":
        session_signal_name = "signal"

        if session.get("signal") is None:
            audio_path = session.get("audio_path")
            #separator = load_separator("spleeter", stems=session.get("stem", 2))
            #signal = separator.separate(audio_path.as_posix())
            import pickle
            with open("signal.pkl", 'rb') as f:
                signal = pickle.load(f)
            session["signal"] = signal
            _save_all(signal)
        elif load_augment:
            session_signal_name += "_augmented"
        else:
            print("POPPING AUGMENTED")
            session.pop("signal_augmented", None)

        signal = session.get(session_signal_name, session.get("signal"))
        names = signal.get_names()
        if "signal_augmented" in session and load_augment:
            names = [f"{n}_augmented" for n in names]

    return render_template("augment.html", title="Augment",
                           names=names, dir=f"/main/data/{session['dir'].stem}",
                           augment=AugmentSignalForm().augment)

@main.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

@main.route("/main/data/<path:subpath>")
def get_audio(subpath):
    return send_from_directory("main/data", subpath)

import uuid
from pathlib import Path

import numpy as np
import soundfile as sf

from werkzeug.utils import secure_filename

from flask import (render_template, request, jsonify,
                   send_from_directory)
from flask import Blueprint, session, redirect, url_for

# package import
from separator import Config
from separator.main.augment import Augment
from separator.main import UploadForm, AugmentForm
from separator.main.separate import SpleeterSeparator
from separator.main import save_audio, save_audio_from_storage

main = Blueprint(name="main", import_name=__name__)
augment = Augment()

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
    form = AugmentForm()
    if form.validate_on_submit():
        pass
    elif request.method == "GET":
        audio_path = session.get("audio_path")
        separator = load_separator("spleeter", stems=session.get("stem", 5))
        #signal = separator.separate(audio_path.as_posix())
        import pickle
        with open("signal.pkl", 'rb') as f:
            signal = pickle.load(f)
            
        session["signal"] = signal

        for name, sig in signal.get_items():
            signal_path = session["dir"] / name
            save_audio(sig, signal_path, session["audio_meta"])
    return render_template("augment.html", form=form, title="Augment",
                           names=signal.get_names(), dir=f"/main/data/{session['dir'].stem}")

@main.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

@main.route("/main/data/<path:subpath>")
def get_audio(subpath):
    return send_from_directory("main/data", subpath)

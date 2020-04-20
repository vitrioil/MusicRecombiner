import numpy as np
import soundfile as sf

from werkzeug.utils import secure_filename

from flask import render_template, request, jsonify
from flask import Blueprint, session, redirect, url_for

# package import
from separator.main import save_audio
from separator.main import UploadForm, AugmentForm
from separator.main.augment import Augment
from separator.main.separate import SpleeterSeparator

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
        audio_file = request.files.get("audio")
        audio = save_audio(audio_file)

        session["audio"] = audio
        session["stem"] = form.stems.data

        return redirect(url_for("main.augment"))
    return render_template("home.html", form=form, title="Home")

@main.route("/augment", methods=["GET", "POST"])
def augment():
    form = AugmentForm()
    if form.validate_on_submit():
        pass
    elif request.method == "GET":
        audio = session.get("audio")
        separator = load_separator("spleeter", stems=session.get("stem", 5))
        signal = separator.separate(audio)
    return render_template("augment.html", form=form, title="Augment")

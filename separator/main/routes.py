from flask import Blueprint, session, redirect
from flask import render_template, request, jsonify

# package import
from separator.main import UploadForm
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
        session["audio"] = request.files.get("audio").read()
        session["stem"] = form.stems.data
        return redirect(url_for("augment"))
    return render_template("home.html", form=form, title="Home")

@main.route("/augment", methods=["GET", "POST"])
def augment():
    form = AugmentForm()

    if form.validate_on_submit():
        pass

    return render_template("augment.html", form=form, title="Augment")

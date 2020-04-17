from flask import Blueprint
from flask import render_template, request, jsonify

# package import
from separator.main.augment import Augment
from separator.main.separate import SpleeterSeparator

main = Blueprint("main", __name__)
augment = Augment()

def load_separator(separator_name: str, *args, **kwargs):

    if separator_name.lower() == "spleeter":
        separator = SpleeterSeparator(*args, **kwargs)

    return separator

separator = load_separator("spleeter")

@main.route("/separate/<int:stem>", methods=["POST"])
def main(stem):
    pass

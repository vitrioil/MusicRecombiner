from flask import Blueprint
from flask import render_template, request, jsonify


main = Blueprint("main", __name__)
ner = NER()


@main.route("/separate/<int:stem>", methods=["POST"])
def main(stem):
    pass

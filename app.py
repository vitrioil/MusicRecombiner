import os
from argparse import ArgumentParser

#package import
from separator import create_config_app

app = create_config_app()

def create_db():
    print("Creating database")
    from separator import db
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--create-db", '-c', action="store_true", dest="create_db")
    args = parser.parse_args()

    if args.create_db:
        create_db()
    app.run(debug=True, host="0.0.0.0")

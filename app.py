import os

#package import
from separator import create_config_app

app = create_config_app()


if not os.path.exists("separator/storage.db"):
    print("Creating database")
    from separator import db
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

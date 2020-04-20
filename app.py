from separator import create_config_app

app = create_config_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

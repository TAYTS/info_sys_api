from app import make_app

app = make_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0')

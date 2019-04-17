from app import app

if __name__ == "__main__":
    app.debug=True
    app.run(host="172.16.0.4", port=80)

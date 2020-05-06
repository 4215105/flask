#! venv/bin/python
from app import app

if __name__ == "__main__":
    app.debug=True
    app.run(host="172.30.0.9", port=80)

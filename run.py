from flask import jsonify
from app.routes import app


if __name__ == '__main__':
    app.run(debug=False, port=5000)
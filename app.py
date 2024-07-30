from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from api.strategy_api import strategy
from api.common_api import common
# from database.database import db
import json

app = Flask(__name__)
app.register_blueprint(strategy)
app.register_blueprint(common)


# db.init_app(app)

CORS(app, supports_credentials=True)  # 允许跨域访问

if __name__ == '__main__':

    app.run(debug=True)

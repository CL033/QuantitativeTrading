from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from api.strategy_api import strategy

app = Flask(__name__)
app.register_blueprint(strategy)

CORS(app, supports_credentials=True)  # 允许跨域访问

if __name__ == '__main__':
    app.run(debug=True)

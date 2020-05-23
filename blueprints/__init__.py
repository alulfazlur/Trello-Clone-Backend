
import hashlib
from datetime import timedelta
from functools import wraps
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims

import json
import config
import os
import jwt
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_cors import CORS

app = Flask(__name__)
flaskenv = os.environ.get('FLASK_ENV', 'Production')
if flaskenv == "Production":
    app.config.from_object(config.ProductionConfig)
elif flaskenv == "Testing":
    app.config.from_object(config.TestingConfig)
else:
    app.config.from_object(config.DevelopmentConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

jwt = JWTManager(app)
CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True, intercept_exceptions=False)

def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['id'] is None:
            return {'status': 'FORBIDDEN', 'message': 'Internal only'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper


@app.before_request
def before_request():
    if request.method != 'OPTIONS':
        pass
    else:
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': '*'}


@app.after_request
def after_request(response):
    try:
        requestData = request.get_json()
    except Exception as e:
        requestData = request.args.to_dict()
    if response.status_code == 200:
        app.logger.warning("REQUEST_LOG\t%s", json.dumps({
            'method': request.method,
            'code': response.status,
            'uri': request.full_path,
            'request': requestData,
            'response': json.loads(response.data.decode('utf-8'))
        })
        )
    else:
        app.logger.error("REQUEST_LOG\t%s", json.dumps({
            'method': request.method,
            'code': response.status,
            'uri': request.full_path,
            'request': requestData,
            'response': json.loads(response.data.decode('utf-8'))
        })
        )

    return response

from blueprints.auth import bp_auth
from blueprints.user.resources import bp_user
from blueprints.board.resources import bp_board
from blueprints.list.resources import bp_list
from blueprints.card.resources import bp_card

app.register_blueprint(bp_auth, url_prefix='/login')
app.register_blueprint(bp_user, url_prefix='/user')
app.register_blueprint(bp_board, url_prefix='/board')
app.register_blueprint(bp_list, url_prefix='/list')
app.register_blueprint(bp_card, url_prefix='/card')

db.create_all()

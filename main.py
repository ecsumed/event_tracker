from flask import Flask
from flask import request
from flask import jsonify

from models import db

app = Flask(__name__)


def error_response(code=-1, error=""):
    """
    Return a JSON string for any error condition.
    """
    return jsonify({
                   "status": code,
                   "error": 1,
                   "error_msg": error
                   })


def success_response(code=1, response=""):
    """
    Return a JSON string for a successful condition.
    """
    return jsonify({
                   "status": code,
                   "response": response
                   })


@app.route('/addEvent', methods=['POST'])
def addEvent():
    """
    API call to add an event.

    INPUT:
        {'cood': '', 'event_time': '', 'event_type': ''}

    OUTPUT:
        Success: 1
        Failure: 2
    """
    return success_response(1, "Added")


import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

db_drop_and_create_all()


## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods={"GET"})
def drinks():
    """Fetch all drinks """

    drinks = [drink.short() for drink in Drink.query.all()]

    return jsonify({"success": True,
                    "drinks": drinks})


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks-detail",  methods={"GET"})
@requires_auth('get:drinks-detail')
def drinks_with_detail(payload):
    """Fetch all drinks with detail"""
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({"success": True,
                    "drinks": drinks})



'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods={"POST"})
@requires_auth('post:drinks')
def new_drink(payload):
    """Created drink"""

    data = request.get_json() 
    recipe = data.get("recipe")

    if type(recipe) is dict: # check if type recipe  is dict
        recipe = [recipe]

    if data.get('title'):  # check recipe and title not none
        drink = Drink(title=data["title"],
                      recipe=json.dumps(recipe))

        drink.insert() 

        return jsonify({"success": True,
                        "drinks": drink.long()})

    abort(422)


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>", methods={"PATCH"})
@requires_auth("patch:drinks")
def updated_drink(payload, id):
    """Updated drink by drinkID """

    drink = Drink.query.filter_by(id=id).one_or_none()
    data = request.get_json()
    title  = data.get("title")
    recipe = data.get("recipe")

    if type(recipe) is dict: # check if type recipe  is dict
        recipe = [recipe]

    if not drink:
        abort(404)

    if title:
        drink.title = title

    if recipe:
        drink.recipe = json.dumps(recipe)

    drink.update()

    return jsonify({"success": True,
                    "drinks": drink.long()})

'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>", methods={"DELETE"})
@requires_auth("delete:drinks")
def deleted_drink(payload, id):
    """Deleted drink by drinkID"""
    
    drink = Drink.query.filter_by(id=id).one_or_none()

    if not drink:
        abort(404)

    drink.delete()

    return jsonify({"success": True,
                    "delete": id})


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    """handler for 422 error"""
    return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
        }), 422

'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''



'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''

@app.errorhandler(404)
def handler_not_found(error):
    """handler for 404 error"""
    return jsonify({
            "success": False, 
            "error": 404,
            "message": "Resource not found"
        }), 422



'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def handler_auth_error(error):
    """handler for auth error"""
    return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

@app.errorhandler(401)
def handler_unauthorized(error):
    """handler for 401 error"""
    return jsonify({
            "success": False,
            "error": 401,
            "message": 'Unathorized'
        }), 401

@app.errorhandler(405)
def handler_method_not_allowed(error):
    """handler for 405 error"""
    return jsonify({
            "success": False,
            "error": 405,
            "message": 'Method Not Allowed'
        }), 405


@app.errorhandler(400)
def handler_bad_request(error):
    """handler for 400 error"""
    return jsonify({
            "success": False,
            "error": 400,
            "message": 'Bad Request'
        }), 400
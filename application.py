from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging
from datetime import datetime
from application_services.user_resource import UserResource
import copy

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

##################################################################################################################

@app.route('/api', methods=['GET'])
def home():
    # TODO: Add google authorized case
    return "Welcome to HireTracker"

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    # get all users
    if request.method == 'GET':
        result = UserResource.get_all_users(request.args)
        return Response(json.dumps(result, default=str), status=200, content_type="application/json")

    # create a user
    elif request.method == 'POST':
        request_data = request.get_json()
        print(request_data)
        email = request_data.get('email', None)
        if email is None:
            return Response(json.dumps("Email missing.", default=str), status=400, content_type="application/json")
        if UserResource.exists_by_email(email):
            return Response(json.dumps("Email already existed. Please use another email.", default=str), \
                            status=401, content_type="application/json")
        data = {}
        for k in request_data:
            if request_data[k] is not None:
                data[k] = request_data[k]

        column_name_list = []
        value_list = []
        for k, v in data.items():
            column_name_list.append(k)
            value_list.append(v)
        user_id = UserResource.add_by_user_attributes(column_name_list, value_list)
        return Response(json.dumps(f"User added with user_id {user_id}", default=str), \
                       status=200, content_type="application/json")

    else:
        return Response(json.dumps("Bad request. Wrong method", default=str), \
                        status=410, content_type="application/json")

@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def certain_user(user_id):
    # get a user
    if request.method == 'GET':
        try:
            result = UserResource.get_by_user_id(user_id)
        except:
            return Response(json.dumps("Invalid fields requested!", default=str), \
                            status=401, content_type="application/json")
        if len(result) != 0:
            result = result[0]
            return Response(json.dumps(result, default=str), status=200, content_type="application/json")
        else:
            return Response(json.dumps(f"User with user_id {user_id} not found!", default=str), \
                            status=404, content_type="application/json")
    # Update a user
    elif request.method == 'PUT':
        request_data = request.get_json()
        UserResource.update_by_user_id(user_id, **request_data)

        return Response(json.dumps(f"User updated with user_id {user_id}", default=str), \
                        status=200, content_type="application/json")

    # Delete a user
    elif request.method == 'DELETE':
        result = UserResource.delete_by_user_id(user_id)
        return Response(json.dumps(f"User deleted with user_id {user_id}", default=str), \
                       status=201, content_type="application/json")
    else:
        return Response(json.dumps("Bad request. Wrong method", default=str), \
                        status=410, content_type="application/json")

# @app.route('/api/google_auth', methods=['GET'])
# def google_authorization():
    # TODO: add login with google authorization in sprint2
    # Logic:
    # if google.authorized:
    #   get email from google.data
    #   get user_id from UserResource.get_user_id_by_email(email)
    #   if user_id exists:
    #       return redirect('/api/users/{}'.format(uid["user_id"]))
    #   else:
    #       redirect to "create profile" page??
    # else:
    #   redirect to google login?

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
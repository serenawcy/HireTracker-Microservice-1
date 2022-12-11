from flask import Flask, Response, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
import json
import os
from oauthlib.oauth2 import TokenExpiredError
from application_services.user_resource import UserResource
import middleware.security as security

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.config['SECRET_KEY'] = security.SECRET_KEY
app.config['CORS_HEADERS'] = 'Content-Type'
client_id = "688341703537-ud62buo4s3cia88o3ldiru6udrl8ug56.apps.googleusercontent.com"
client_secret = "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"

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
blueprint = make_google_blueprint(
    client_id=client_id,
    # client_secret=client_secret,
    client_secret = "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",
    reprompt_consent=True,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")
google_blueprint = app.blueprints.get("google")

CORS(app)

##################################################################################################################
# Homepage
@app.before_request
def before_request_func():
    result = security.check_security(request, google, blueprint)
    if not result:
        return redirect(url_for("google.login"))

@app.route('/', methods=['GET'])
def homepage():
    if google.authorized: # after login
        user_data = google.get('oauth2/v2/userinfo').json()
        email = user_data['email']
        user_info = UserResource.get_user_id_by_email(email)
        if user_info is None: # user doesn't exist
            return render_template('signup.html', email=email)
        else: # user already exist
            return redirect('/api/users/{}'.format(user_info[0]["user_id"]))
    else:
        return render_template('signin.html')

@app.route('/api/google-login', methods=['GET'])
def google_login():
    return redirect("/")

@app.route('/api/signup', methods=['POST'])
def signup():
    if google.authorized:  # after login
        user_data = google.get('oauth2/v2/userinfo').json()
        email = user_data['email']
    request_data = request.form
    nickname = request_data.get('nickname', None)
    if email is None:
        return Response(json.dumps("Email missing.", default=str), status=400, content_type="application/json")
    if nickname is None:
        return Response(json.dumps("Nickname missing.", default=str), status=400, content_type="application/json")
    if UserResource.exists_by_email(email):
        return Response(json.dumps("Email already existed. Please use another email.", default=str), \
                        status=401, content_type="application/json")

    insert_data = {}
    for k in request_data:
        if request_data[k] is not None:
            insert_data[k] = request_data[k]
    insert_data["email"] = email
    column_name_list = []
    value_list = []
    for k, v in insert_data.items():
        column_name_list.append(k)
        value_list.append(v)
    user_id = UserResource.add_by_user_attributes(column_name_list, value_list)
    return redirect('/api/users/{}'.format(user_id))

@app.route('/api/users', methods=['GET'])
def users():
    # get all users
    if request.method == 'GET':
        result = UserResource.get_all_users(request.args)
        return Response(json.dumps(result, default=str), status=200, content_type="application/json")

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
@app.route("/api/logout")
def logout():
    token = blueprint.token["access_token"]
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    del blueprint.token  # Delete OAuth token from storage
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
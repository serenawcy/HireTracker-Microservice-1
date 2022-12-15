import json

# Need Login
insecure_paths = [
    '/api/google-login',
    '/api/signup'
]

SECRET_KEY = "hello"

def check_security(request, google, blueprint):
    path = request.path
    result = False

    if path in insecure_paths: # need check authentication
        google_data = None

        user_info_endpoint = '/oauth2/v2/userinfo'
        if google.authorized:
            google_data = google.get(user_info_endpoint).json()

            print(json.dumps(google_data, indent=2))

            session = blueprint.session
            token = session.token
            print("Token = \n", json.dumps(token, indent=2))

            result = True
    else:
        result = True

    return result
from app import app, CLIENT_ID
from app.models import User
from flask import render_template, request, session, jsonify, flash
import requests

# google authentication
import string
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


def json_response(message, status_code):
    response = jsonify(message=message)
    response.status_code = status_code
    return response


def generate_session_token():
    """
    Generates a random string to prevent forgery thing
    when authenticating with oauth
    :return: random string
    """
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(32)
    )


@app.route('/login')
def login():
    session['state'] = generate_session_token()

    return render_template(
        'login.html',
        state=session['state']
    )


def check_state():
    req_state = request.json.get('state')
    login_state = session['state']

    return req_state == login_state


def get_credentials():
    one_time_code_from_client = request.json.get('code')
    oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'

    return oauth_flow.step2_exchange(one_time_code_from_client)


def check_credentials_with_oauth(credentials_access_token, credentials_gplus_id):
    """
    Get oauth info with access token
    and compare it with credentials values
    :param credentials:
    :return:
    """
    oauth_url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(credentials_access_token)
    oauth_req = requests.get(oauth_url)
    oauth_json = oauth_req.json()

    # check for error field
    oauth_error = oauth_json.get('error')

    if oauth_error:
        return False, json_response(oauth_error, 500)

    # compare user ids
    oauth_user_id = oauth_json['user_id']

    if oauth_user_id != credentials_gplus_id:
        error_message = 'Token\'s user ID({}) doesn\'t match given user ID.({})'.format(
            oauth_user_id,
            credentials_gplus_id
        )
        return False, json_response(error_message, 401)

    # check client id
    if oauth_json['issued_to'] != CLIENT_ID:
        error_message = 'Token\'s client ID does not match app\'s.{} vs {}'.format(oauth_json['issued_to'], CLIENT_ID)
        return False, json_response(error_message, 401)

    return True, None


def is_already_authenticated(gplus_id):
    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')

    return stored_access_token is not None and gplus_id == stored_gplus_id


def get_google_userinfo(access_token):
    USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    answer = requests.get(
        USER_INFO_URL,
        params={
        'access_token': access_token,
        'alt': 'json'
    })

    return answer.json()


def user_from_userinfo(userinfo):
    user = User.from_email(userinfo['email'])

    if not user:
        user = User.create_and_save(
            userinfo['name'],
            userinfo['email']
        )

    return user


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if not check_state():
        return json_response('Invalid session state token', 401)

    try:
        credentials = get_credentials()
    except FlowExchangeError:
        return json_response('Couldnt\' upgrade authorizzation code', 401)

    access_token = credentials.access_token
    gplus_id = credentials.id_token['sub']

    ok, error_response = check_credentials_with_oauth(access_token, gplus_id)

    if not ok:
        return error_response

    if is_already_authenticated(gplus_id):
        return json_response('Current user is already connected.', 200)

    # save authentication data
    session['access_token'] = access_token
    session['gplus_id'] = gplus_id

    data = get_google_userinfo(access_token)
    user = user_from_userinfo(data)
    session['user_id'] = user.id
    session['email'] = user.email
    session['picture'] = data['picture']

    flash("You're logged as {} (google account)".format(user.username))

    return jsonify(
        username=user.username,
        picture=data['picture']
    )


def is_logged_in():
    return 'user' in session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = session['access_token']

    if not access_token:
        print('no access token')
        return json_response('Have no access token', 401)

    print('gdisconnect(): access token is {}'.format(access_token))
    print('User name: {}'.format(session['user'].name))

    respo = requests.post(
        'https://accounts.google.com/o/oauth2/revoke',
        params={'token': access_token},
        headers={'content-type': 'application/x-www-form-urlencoded'}
    )

    if respo.status_code == 200:
        session.clear()
        return json_response('Successfully disconnected.', 200)
    else:
        print(respo)
        print(respo.text)
        session.clear()
        return json_response('Failed to revoke token for given user', respo.status_code)
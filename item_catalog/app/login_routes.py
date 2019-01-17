from flask import render_template, session, flash, url_for
from flask import request, jsonify, redirect
from flask_login import current_user, login_user, logout_user
import requests
from app import app, CLIENT_ID, login
from app.models import User
from app.forms import LoginForm

# google authentication
import string
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


@login.user_loader
def load_user(id_str):
    return User.query.get(int(id_str))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('show_items'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("You logged in as {}".format(user.username))
            return redirect(url_for('show_items'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    session['state'] = generate_session_token()

    return render_template(
        'login.html',
        title='Sign In',
        state=session['state'],
        form=form
    )


@app.route('/logout', methods=['POST'])
def logout():
    gdisconnect()
    logout_user()
    session.clear()
    return "true"


# google oauth
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


def check_state():
    req_state = request.json.get('state')
    login_state = session['state']

    return req_state == login_state


def exchange_auth_code(auth_code):
    oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'

    return oauth_flow.step2_exchange(auth_code)


def check_credentials_with_oauth(
        credentials_access_token,
        credentials_gplus_id):
    """
    Get oauth info with access token
    and compare it with credentials values
    :param credentials_access_token: the access token from the credentials
    obtained from google
    :param credentials_gplus_id: the google id from credentials
    obtained from google
    :return:
    """
    oauth_url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=' + credentials_access_token
    oauth_req = requests.get(oauth_url)
    oauth_json = oauth_req.json()

    # check for error field
    oauth_error = oauth_json.get('error')

    if oauth_error:
        return False, json_response(oauth_error, 500)

    # compare user ids
    oauth_user_id = oauth_json['user_id']

    if oauth_user_id != credentials_gplus_id:
        error_message = "Token's user ID({}) doesn't match given user ID.({})".format(
            oauth_user_id,
            credentials_gplus_id
        )
        return False, json_response(error_message, 401)

    # check client id
    if oauth_json['issued_to'] != CLIENT_ID:
        error_message = "Token's client ID does not match app's.{} vs {}".format(
            oauth_json['issued_to'],
            CLIENT_ID
        )
        return False, json_response(error_message, 401)

    return True, None


def is_already_authenticated(gplus_id):
    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')

    return stored_access_token is not None and gplus_id == stored_gplus_id


def fetch_google_userinfo(access_token):
    USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    answer = requests.get(
        USER_INFO_URL,
        params={
            'access_token': access_token,
            'alt': 'json'
        }
    )

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
        credentials = exchange_auth_code(request.json.get('code'))
    except FlowExchangeError:
        return json_response('Couldnt\' upgrade authorization code', 401)

    access_token = credentials.access_token
    gplus_id = credentials.id_token['sub']

    ok, error_response = check_credentials_with_oauth(access_token, gplus_id)

    if not ok:
        return error_response

    if is_already_authenticated(gplus_id):
        user = User.query.filter_by(id=session['user_id']).one()
        return jsonify(
            username=user.username,
            picture=session['picture'],
            message='Current user is already connected.'
        )

    # save authentication data
    session['access_token'] = access_token
    session['gplus_id'] = gplus_id

    data = fetch_google_userinfo(access_token)
    user = user_from_userinfo(data)
    session['user_id'] = user.id
    session['email'] = user.email
    session['picture'] = data['picture']
    login_user(user)

    flash("You're logged as {} (google account)".format(user.username))

    return jsonify(
        message='successful authentication',
        username=user.username,
        picture=data['picture']
    )


def gdisconnect():
    access_token = session.get('access_token')

    if access_token:
        print('gdisconnect(): access token is {}'.format(access_token))
        print('User name: {}'.format(session['user'].name))

        disconnect_response = requests.post(
            'https://accounts.google.com/o/oauth2/revoke',
            params={'token': access_token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )

        if disconnect_response.status_code != 200:
            print('gdisconnect error')
            print(disconnect_response)
            print(disconnect_response.text)

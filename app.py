from flask import Flask, request, make_response,render_template, session,jsonify
from datetime import datetime , timedelta, timezone
from functools import wraps

import jwt
app = Flask(__name__)
app.config['SECRET_KEY'] = "ejer3043492qekddce9492230rfk"

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'token':'token is missing'})
        try:
            payload = jwt.decode(token, app.config(['SECRET_KEY']),algorithms= ['HS256'])
        except:
             return jsonify({'Alert':'invalid token!'})
    return decorated


@app.route('/public')
def public():
    return "this is a public section"

@app.route('/auth')
@token_required
def auth():
    return "this is authenticated section"
@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template('login1.html')
    else:
        return " you are logged-in"

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('username') and request.form.get('password') == '123456':
        session['logged_in'] = True
        token = jwt.encode(
               {
                'user': request.form.get('username'),
                'expiration': str(datetime.now(timezone.utc)+timedelta(seconds =160))

                 },
                app.config['SECRET_KEY'],
                 algorithm= 'HS256'
               )
        return jsonify({'token': token})
    else:
        make_response("unable to verify", 403)


if __name__=='__main__':
    app.run(debug=True)









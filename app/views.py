from app import app, api, mktorest, models, lm
from flask_restful import Resource, reqparse
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import render_template
import os
from datetime import datetime

# Init rest client on import
# setvars.py should be maintained locally containing restcreds dictionary
try:
	from app import setvars
	restClient = mktorest.MarketoWrapper(setvars.restcreds['munchkin_id'], 
										 setvars.restcreds['client_id'], 
										 setvars.restcreds['client_secret'])
	apiKey = setvars.apiKey
except ImportError:
	restClient = mktorest.MarketoWrapper(os.environ['munchkin_id'], os.environ['client_id'], os.environ['client_secret'])
	apiKey = os.environ['apiKey']

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if g.user is not None and g.user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         session['remember_me'] = form.remember_me.data
#         return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
#     return render_template('login.html', 
#                            title='Sign In',
#                            form=form,
#                            providers=app.config['OPENID_PROVIDERS'])

@app.route('/')
def index():
		return render_template('index.html')

@app.route('/base')
def base():
		return render_template('base.html')
		
@app.route('/get-started-b2b')
def get_started_b2b():
    return render_template('get-started-b2b.html')




class CreateFolders(Resource):
	def get(self, api_key_in, new_email):
		if api_key_in != apiKey or '@' not in new_email:
			return {'success':False}
		else:
			results = []
			foldername = new_email.split('@')[0].lower()
			for parentId in [19802,19801,19799,19797,19798,19794,19795,19791,19790]:
				trialcounter=0
				while trialcounter<3:
					try:
						create_result = restClient.create_folder(foldername, str(parentId))
						print(create_result)
						if create_result['success']:
							results.append(create_result['result'][0]['id'])
						else:
							results.append(create_result['errors'])
						break
					except Exception as e:
						print(e)
						trialcounter+=1
						if trialcounter==3:
							results.append('Unknown Error')
			return {'success':True,'folder_name': foldername,'results':results}

api.add_resource(CreateFolders, '/createfolders/<string:api_key_in>/<string:new_email>')


rl_parser = reqparse.RequestParser()
rl_parser.add_argument('firstName')
rl_parser.add_argument('lastName')
rl_parser.add_argument('email', required=True)
rl_parser.add_argument('accountString', required=True)
rl_parser.add_argument('pod',required=True)
rl_parser.add_argument('loginDate')

#Endpoint to track who is using mktolive - pass in first/last/email-of-user-id/account-string/pod/(I infer current login date or accept login date)
#may be taking in marketo munchkin ID and not pod, but need one of the two
# class RecordLogin(Resource):
# 	def post(self, api_key_in):
# 		args=rl_parser.parse_args()
# 		if 'loginDate' not in args:
# 			login_date=datetime.utcnow()
# 		else:
# 			login_date=datetime.fromtimestamp(args['loginDate'], timezone.utc)
# 		user = models.User.query.filter_by(email=args['email']).first()
# 		if not user:
# 			user = models.User()
# 			user.first_name = args['firstName']
# 			user.last_name = args['lastName']
# 			user.email = args['email']
# 			#eventually: here we will query the marketo instance with the user db to populate the rest of the fields
# 		sub = user.subscriptions.filter_by(account_string=args['accountString']).first()
# 		if not sub:
# 			sub = models.Subscription()
# 			sub.mkto_pod = args['pod']
# 			sub.account_string = args['accountString']
# 		sub.last_login = login_date


# This was an example for pope on how to serve robots.txt, we may use it later
# @app.route('/robots.txt')
# def sendrobot():
# 	return app.send_static_file('robots.txt')
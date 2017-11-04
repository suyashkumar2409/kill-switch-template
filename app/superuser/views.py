from flask import render_template, redirect, request, url_for, flash, current_app
from . import superuser
from flask_login import login_required, login_user, logout_user, current_user
from ..models import User, Request, Role
# from .forms import LoginForm, RegistrationForm
from ..email import send_email
from app import db
from .forms import UpgradeForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@superuser.route('/upgrade/', methods=['GET', 'POST'])
@login_required
def upgrade():
	form = UpgradeForm()

	if form.validate_on_submit():
		print "lol"
		# send email and add request row
		if form.upgradeToCreater.data:
			requestUpgrade = Request()
			requestUpgrade.role_id = Role.query.filter_by(permissions = 2).first().id
			requestUpgrade.user_id = current_user.get_id()
			requestUpgrade.status = 0


			db.session.add(requestUpgrade)
			db.session.commit()
			
			user = current_user
			token = user.generate_token_role(role = 2, requestId = requestUpgrade.request_id)
			send_email(current_app.config['APP_MAIL_SENDER'], 'Upgrade to Quiz Creator', 'superuser/email/confirmCreator', user = user, token = token)
			flash('A request mail for becoming quiz creator has been sent to the admin')

			print('creator')

		elif form.upgradeToSuperUser.data:
			requestUpgrade = Request()
			requestUpgrade.role_id = Role.query.filter_by(permissions = 4).first().id
			requestUpgrade.user_id = current_user.get_id()
			requestUpgrade.status = 0

			db.session.add(requestUpgrade)
			db.session.commit()

			user = current_user
			token = user.generate_token_role(role = 4, requestId = requestUpgrade.request_id)
			send_email(current_app.config['APP_MAIL_SENDER'], 'Upgrade to Super User', 'superuser/email/confirmSuperUser', user = user, token = token)
			flash('A request mail for becoming Super User has been sent to the admin')

			print('super')

		return render_template('index.html')
		return redirect(url_for('main.index'))


	else:
		print "bbbbob"
		buttonData = {}
		# get possible request row entry and render form
		requests = Request.query.filter_by(user_id = current_user.get_id())
		creatorRequest = requests.filter_by(role_id = Role.query.filter_by(permissions = 2).first().id).first()
		if creatorRequest:
			# print "yo"
			if creatorRequest.status == 0:
				buttonData['upgradeToCreaterLabel'] = 'Request sent'
				buttonData['upgradeToCreaterId'] = 'disabledButton'

			elif creatorRequest.status == 1:
				buttonData['upgradeToCreaterLabel'] = 'Request accepted'
				buttonData['upgradeToCreaterId'] = 'disabledButton'

			elif creatorRequest.status == 2:
				buttonData['upgradeToCreaterLabel'] = 'Request declined'
				buttonData['upgradeToCreaterId'] = 'disabledButton'
		
		else:
			print "yeah"
			buttonData['upgradeToCreaterLabel'] = 'Upgrade to Quiz creator'
			buttonData['upgradeToCreaterId'] = 'enabledButton'

		superUserRequest = requests.filter_by(role_id = Role.query.filter_by(permissions = 4).first().id).first()
		if superUserRequest:
			if superUserRequest.status == 0:
				buttonData['upgradeToSuperUserLabel'] = 'Request sent'
				buttonData['upgradeToSuperUserId'] = 'disabledButton'

			elif superUserRequest.status == 1:
				buttonData['upgradeToSuperUserLabel'] = 'Request accepted'
				buttonData['upgradeToSuperUserId'] = 'disabledButton'

			elif superUserRequest.status == 2:
				buttonData['upgradeToSuperUserLabel'] = 'Request declined'
				buttonData['upgradeToSuperUserId'] = 'disabledButton'

		else:
			buttonData['upgradeToSuperUserLabel'] = 'Upgrade to Super User'
			buttonData['upgradeToSuperUserId'] = 'enabledButton'
			
		return render_template('superuser/requestUpgrade.html', form = form, buttonData = buttonData)

			# elif creatorRequest.first().status == 1:
			# 	form.upgradeToCreater.
			# means request for quiz creator has been sent

def errInLoading():
	flash('Incorrect link!')
	return redirect(url_for('main.index'))

@superuser.route('/confirm/<token>')
@login_required
def confirm(token):
	s = Serializer(current_app.config['SECRET_KEY'])
	try:
		data = s.loads(token)
		print (data)

		userId = data.get('confirm')
		rolePermission = data.get('role')
		requestId = data.get('requestId')
		
		user = User.query.filter_by(id = userId).first()
		# print(user)
		role = Role.query.filter_by(permissions = rolePermission).first()
		# print(role)
		
		request = Request.query.filter_by(request_id = requestId).first()
		# print (request)
		# return errInLoading()
        

		if user is not None and role is not None and request is not None:
			user.role_id = role.id
			db.session.add(user)
			request.status = 1
			db.session.add(request)

			print user.role_id

			flash('This user has been approved')
			return redirect(url_for('main.index'))
		else:
			return errInLoading()
	except:
		print('loads didnt work')
		return errInLoading()


@superuser.route('/decline/<token>')
@login_required
def decline(token):
	s = Serializer(current_app.config['SECRET_KEY'])
	try:
		data = s.loads(token)
		print (data)

		userId = data.get('confirm')
		rolePermission = data.get('role')
		requestId = data.get('requestId')
		
		user = User.query.filter_by(id = userId).first()
		# print(user)
		role = Role.query.filter_by(permissions = rolePermission).first()
		# print(role)
		
		request = Request.query.filter_by(request_id = requestId).first()
		# print (request)
		# return errInLoading()
        

		if user is not None and role is not None and request is not None:
			request.status = 2
			db.session.add(request)

			print user.role_id

			flash('This user has been declined')
			return redirect(url_for('main.index'))
		else:
			return errInLoading()
	except:
		print('loads didnt work')
		return errInLoading()

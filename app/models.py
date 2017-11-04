from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer, index = True)

    requests = db.relationship('Request', backref='roleRequestList', lazy = 'dynamic')
    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default = 1)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default = False)

    requests = db.relationship('Request', backref='userRequestList', lazy = 'dynamic')


    def generate_confirmation_token(self, expiration = 60*60*48):
    	s = Serializer(current_app.config['SECRET_KEY'], expiration)
    	return s.dumps({'confirm':self.id})

    def generate_token_role(self, expiration = 60*60*48, role = 2, requestId = -1):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id, 'role':role, 'requestId':requestId})

    def confirm(self, token):
    	s = Serializer(current_app.config['SECRET_KEY'])
    	try:
    		data = s.loads(token)
    	except:
            print('loads didnt work')
            return False
    	if data.get('confirm') != self.id:
            print(data.get('confirm'))
            print(self.id)
            return False

        self.confirmed = True
        db.session.add(self)
        return True

 	   	
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class Request(db.Model):
    __tablename__ = 'requests'

    request_id = db.Column(db.Integer, primary_key = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True)
    status = db.Column(db.Integer)
    # status - 0, sent, 1, accepted, 2 declined
class Permission:
    ATTEMPT = 0x01
    CREATE = 0x02
    SHUTDOWN = 0x04
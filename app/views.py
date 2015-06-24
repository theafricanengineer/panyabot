from flask import render_template, url_for, request, g, flash, redirect
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, bcrypt
from .forms import LoginForm, RegistrationForm
from .models import User, Robot

@app.before_request
def before_request():
	g.user = current_user

@login_manager.user_loader
def user_loader(user_id):
	return User.query.get(int(user_id))

@app.route('/register', methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		print "Registering User.."
		pwd_hash=bcrypt.generate_password_hash(form.password.data)
		# print ('Firstname=%s, Lastname=%s, Nickname=%s, Robot Name=%s, Robot MAC=%s, Robot Owner=%s' % (form.firstname.data
		# 	,form.lastname.data, form.nickname.data, form.robot_name.data, form.robot_mac.data, form.nickname.data))
		user = User(firstname=form.firstname.data, lastname=form.lastname.data, nickname=form.nickname.data, password=pwd_hash)
		db.session.add(user)
		robot = Robot(alias=form.robot_name.data, macid=form.robot_mac.data, owner=User.query.filter_by(nickname=(form.nickname.data)).first())
		db.session.add(robot)
		db.session.commit()
		flash('You\'re account has been created. Please log in')
		return redirect(url_for('login'))
	return render_template('register.html', title='Sign Up', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('home'))	
	print db
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(nickname=form.nickname.data).first()
		print user
		if user:
			if bcrypt.check_password_hash(user.password, form.password.data):
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=form.remember_me.data)
				flash('Welcome %s' % (g.user.nickname))
				return redirect(request.args.get('next') or url_for('home'))
			else:
				flash('Invalid login. Please try again')	
		else:
			flash('Invalid login. Please try again')
			return redirect(url_for('login'))
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	"""Logout the current user"""
	user=current_user
	user.authenticated=False
	db.session.add(user)
	db.session.commit()
	logout_user()
	return redirect(url_for('login'))

@app.route('/')
@app.route('/home')
@login_required
def home():
	user = g.user
	return render_template('home.html', title='Home', user=user)
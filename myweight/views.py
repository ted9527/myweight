import datetime

from flask import  render_template, request,url_for,flash,redirect
from flask_login import login_user,login_required,logout_user,current_user
from sqlalchemy import desc

from myweight import app, db
from myweight.models import User, EverydayWeight
from myweight.forms import LoginForm, LogWeightForm, SignupForm

@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:  # 如果当前用户未认证
        user = {'username': 'Miguel'}
        return render_template('index.html')
    else:
        user = current_user  #User.query.first()
        if request.method == 'POST':
            if not current_user.is_authenticated:  # 如果当前用户未认证
                return redirect(url_for('index'))  # 重定向到主页
        logWeightForm = LogWeightForm()
        everydayWeights = EverydayWeight.query.filter_by(username=user.username).order_by(desc(EverydayWeight.date)).all()[:6]
        
        if request.method == 'POST':
            if not logWeightForm.validate_on_submit():
                flash('Invalid input.')
                return redirect(url_for('index'))  # 重定向回主页
            weight = logWeightForm.todayweight.data #request.form.get('weight')
            if weight == "":
                weight = 65.0
            todayDate = datetime.date.today()
            todayDate = datetime.datetime.combine(todayDate, datetime.time())
            exist = 0
            for myEverydayWeight in everydayWeights:
                if  myEverydayWeight.date == todayDate:
                    exist = 1
                    flash('Today\'s item exists.')
                    break
            if exist == 0:
                todayWeight = EverydayWeight(username=user.username,date=todayDate,weight=weight)
                db.session.add(todayWeight)  # 添加到数据库会话
                db.session.commit()  # 提交数据库会话
                flash('Item created.')  # 显示成功创建的提示
                return redirect(url_for('index'))  # 重定向回主页
            else:    
                return redirect(url_for('index'))  # 重定向回主页
        return render_template('index.html',user=user,weights=everydayWeights,form=logWeightForm)

@app.route('/movie/delete/<int:weight_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required
def delete(weight_id):
    weight = EverydayWeight.query.get_or_404(weight_id)  # 获取电影记录
    db.session.delete(weight)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data 
        user = User.query.filter_by(username=username).first()
        if user is None or not user.validate_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html',title='Sign In', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if request.method == 'POST' and not form.validate_on_submit():
        flash("Password not the same!")
    if request.method == 'POST' and form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('signup.html',title='Sign Up', form=form)

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页


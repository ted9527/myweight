import datetime
from datetime import datetime

from flask import  render_template, request, url_for, flash, redirect, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import desc

from myweight import app, db
from myweight.models import User, EverydayWeight
from myweight.forms import LoginForm, LogWeightForm, SignupForm

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import datetime as dt
import mpld3
import matplotlib.dates as mdates

@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:  # 如果当前用户未认证
        user = {'username': 'Ted'}
        return render_template('index.html')
    else:
        user = current_user 
        if request.method == 'POST':
            if not current_user.is_authenticated:  # 如果当前用户未认证
                return redirect(url_for('index'))  # 重定向到主页
        logWeightForm = LogWeightForm()
        #get the latest 7 days data
        everydayWeights = EverydayWeight.query.filter_by(username=user.username).order_by(desc(EverydayWeight.date)).all()[:7]
        numOfLoggedDays = EverydayWeight.query.filter_by(username=user.username).count()
        
        if request.method == 'POST':
            if not logWeightForm.validate_on_submit():
                flash('Invalid input.')
                return redirect(url_for('index'))  # 重定向回主页
            weight = logWeightForm.todayweight.data #request.form.get('weight')
            if weight == "":
                weight = 65.0
            localDate = request.form['localDate']
            todayDate = datetime.strptime(localDate, '%Y-%m-%d')
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
        return render_template('index.html',totalDays = numOfLoggedDays, weights=everydayWeights,form=logWeightForm)

@app.route('/weight/delete/<int:weight_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required
def delete(weight_id):
    weight = EverydayWeight.query.get_or_404(weight_id)  
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
    if request.method == 'POST' and form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('signup.html',title='Sign Up', form=form)

@app.route('/logout')
@login_required  
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

def getDummy(a,b,n):
    dummyList = []
    if a > b:
        for i in range(1,n):
            dummyList.append(b + (n-i)/n*(a-b) )
    if a <= b:
        for i in range(1,n):
            dummyList.append(a + i/n*(b-a) )
    return dummyList

@app.route('/chart', methods=['GET'])  # 限定只接受 GET 请求
@login_required
def chart():
    if not current_user.is_authenticated:  # 如果当前用户未认证
        user = {'username': 'Ted'}
        return render_template('index.html')
    else:
        user = current_user  
        #取得最近7天的记录 （最多7天，但也可能为0天或者小于7天的数字）
        everydayWeights = EverydayWeight.query.filter_by(username=user.username).order_by(desc(EverydayWeight.date)).all()[:7]
        everydayWeights_normal_order = list(reversed(everydayWeights))  
        numOfLoggedDays = EverydayWeight.query.filter_by(username=user.username).count()
    fig = plt.figure()
    ax2 = fig.add_subplot(111)
    if numOfLoggedDays > 0:
        date1 = everydayWeights_normal_order[0].date  
        date2 = everydayWeights_normal_order[len(everydayWeights_normal_order)-1].date   
        delta = dt.timedelta(days=1)
        date3 =date2 + delta
        days = (date2 - date1).days
        daysnum = len(everydayWeights_normal_order)
        
        y2 = []
        #if only one day record exist
        if daysnum == 1:
            y2 = [everydayWeights_normal_order[0].weight]
            dates2 = date1
        else:
            for i in range(0, daysnum):
                y2.append(everydayWeights_normal_order[i].weight)
                if i == daysnum -1:
                    break
                deltaDays = (everydayWeights_normal_order[i+1].date - everydayWeights_normal_order[i].date).days
                if deltaDays > 1:
                    listD = getDummy(everydayWeights_normal_order[i].weight, everydayWeights_normal_order[i+1].weight, deltaDays) 
                    y2 = y2 + listD
            
            dates2 = mpl.dates.drange(date1, date3, delta)
        ax2.plot_date(dates2, y2, linestyle='-') 

        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        ax2.xaxis.set_major_locator(mdates.DayLocator())
        # Plot
    
        fig.autofmt_xdate(bottom=0.18)
        fig.subplots_adjust(left=0.18)

        plt.gcf().autofmt_xdate()
        plt.savefig("./myweight/static/img/chart.png")

        """    html_str = mpld3.fig_to_html(fig)
        Html_file_before = open("./myweight/templates/chart_before.html","r")
        Html_file_after = open("./myweight/templates/chart_after.html","r")
        Html_file = open("./myweight/templates/chart.html","w")
        html_str_before = Html_file_before.readlines()
        html_str_after = Html_file_after.readlines()
        Html_file.write(str(html_str_before))
        Html_file.write(html_str)
        Html_file.write(str(html_str_after))
        Html_file.close() """

        plt.close()
    return render_template('chart.html', totalDays = numOfLoggedDays)

@app.route('/viewall', methods=['GET'])
@login_required
def viewall():
    if not current_user.is_authenticated:  # 如果当前用户未认证
        user = {'username': 'Ted'}
        return render_template('index.html')
    else:
        user = current_user 
        #get all data
        everydayWeights = EverydayWeight.query.filter_by(username=user.username).order_by(desc(EverydayWeight.date)).all()
        numOfLoggedDays = EverydayWeight.query.filter_by(username=user.username).count()
        return render_template('viewall.html',totalDays = numOfLoggedDays, weights=everydayWeights)

@app.route('/chartall', methods=['GET'])  # 限定只接受 GET 请求
@login_required
def chartall():
    if not current_user.is_authenticated:  # 如果当前用户未认证
        user = {'username': 'Ted'}
        return render_template('index.html')
    else:
        user = current_user  
        #取得所有的记录（但也可能没有记录为0）
        everydayWeights = EverydayWeight.query.filter_by(username=user.username).order_by(desc(EverydayWeight.date)).all()
        everydayWeights_normal_order = list(reversed(everydayWeights))  
        numOfLoggedDays = EverydayWeight.query.filter_by(username=user.username).count()
    fig = plt.figure()
    ax2 = fig.add_subplot(111)
    if numOfLoggedDays > 0:
        date1 = everydayWeights_normal_order[0].date  
        date2 = everydayWeights_normal_order[len(everydayWeights_normal_order)-1].date   
        delta = dt.timedelta(days=1)
        date3 =date2 + delta
        days = (date2 - date1).days
        daysnum = len(everydayWeights_normal_order)
        
        y2 = []
        #if only one day record exist
        if daysnum == 1:
            y2 = [everydayWeights_normal_order[0].weight]
            dates2 = date1
        else:
            for i in range(0, daysnum):
                y2.append(everydayWeights_normal_order[i].weight)
                if i == daysnum -1:
                    break
                deltaDays = (everydayWeights_normal_order[i+1].date - everydayWeights_normal_order[i].date).days
                if deltaDays > 1:
                    listD = getDummy(everydayWeights_normal_order[i].weight, everydayWeights_normal_order[i+1].weight, deltaDays) 
                    y2 = y2 + listD    
            dates2 = mpl.dates.drange(date1, date3, delta)

        ax2.plot_date(dates2, y2, linestyle='-') 

        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        ax2.xaxis.set_major_locator(mdates.DayLocator())
        # Plot
    
        fig.autofmt_xdate(bottom=0.18)
        fig.subplots_adjust(left=0.18)

        plt.gcf().autofmt_xdate()
        plt.savefig("./myweight/static/img/chartall.png")

        plt.close()
    return render_template('chartall.html', totalDays = numOfLoggedDays)





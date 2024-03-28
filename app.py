import os
from datetime import datetime
from flask import Flask, url_for, render_template, request, redirect, session
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Объект класса Flask
app = Flask(__name__)

# секретный ключ приложения
app.secret_key = os.urandom(24)

# По ключу в словаре config устанавливаем в значение программу для работы с БД + название БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация объекта LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Сюда передается обьект на основе класса Flask, подключение к БД уже должно быть выполнено
db = SQLAlchemy(app)


# Построение таблицы
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    # Отображение даты публикации
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # При вызове метода будет выводиться инф. об экземпляре Users и его id
    def __repr__(self):
        return '<Users %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session['username'] = 'Admin'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'Admin' and password == '914Ripazha':
            return redirect(url_for('admin'))
        else:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


# Страница с выводом базы данных
@app.route('/admin')
@login_required
def admin():
    if 'username' not in session:
        return redirect('/login')
    users = Users.query.order_by(Users.date.desc()).all()
    return render_template('admin.html', users=users)


@app.route('/admin/<int:id>')
def detail(id):
    user = Users.query.get(id)
    return render_template('detail.html', user=user)


@app.route('/admin/<int:id>/del')
def delete(id):
    user = Users.query.get_or_404(id)

    try:
        db.session.delete(user)
        db.session.commit()
        return redirect('/admin')
    except:
        return 'DELETION ERROR'


# methods обрабатывает данные из формы(POST) и из прямого перхода на страницу(GET)
@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        user = Users(name=name, email=email, message=message)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return 'ERROR! INVALID DATA!'

    else:
        return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)

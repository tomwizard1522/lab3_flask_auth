from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице необходимо авторизоваться.'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users_db = {
    'user': {'password': 'qwerty'}
}


@login_manager.user_loader
def load_user(user_id):
    if user_id in users_db:
        return User(user_id)
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/counter')
def counter():
    visit_count = session.get('visit_count', 0)
    visit_count += 1
    session['visit_count'] = visit_count

    return render_template('counter.html', count=visit_count)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if username in users_db and users_db[username]['password'] == password:
            user = User(username)
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')


@app.route('/clear-counter')
def clear_counter():
    session.pop('visit_count', None)
    flash('Счетчик посещений сброшен!', 'info')
    return redirect(url_for('counter'))


if __name__ == '__main__':
    app.run(debug=True)
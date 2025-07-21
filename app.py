from flask import Flask, request, redirect, render_template, session, url_for
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Замените на свой ключ в реальном проекте
COMMENTS_FILE = 'comments.json'
USERS_FILE = 'users.json'
LOG_FILE = 'log.txt'

def load_comments():
    if not os.path.exists(COMMENTS_FILE):
        return []
    with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_comment(comment):
    comments = load_comments()
    comments.append(comment)
    with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user(username, password):
    users = load_users()
    users[username] = generate_password_hash(password)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def check_user(username, password):
    users = load_users()
    if username in users and check_password_hash(users[username], password):
        return True
    return False

def log_action(action, username=None, details=None):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = username if username else '-'
        line = f"[{time}] {action} | user: {user}"
        if details:
            line += f" | {details}"
        f.write(line + '\n')

SPORTS = [
    {"name": "Футбол", "slug": "football", "desc": "Футбол — самая популярная командная игра с мячом.", "events": ["Евро-2024: Испания — чемпион!", "Чемпионат России: Зенит — лидер"]},
    {"name": "Баскетбол", "slug": "basketball", "desc": "Баскетбол — динамичная игра с мячом и кольцом.", "events": ["NBA: Финал сезона", "Евролига: ЦСКА — победитель"]},
    {"name": "Теннис", "slug": "tennis", "desc": "Теннис — ракеточный вид спорта на корте.", "events": ["Уимблдон: Новак Джокович — чемпион", "Australian Open: Медведев в финале"]},
    {"name": "Хоккей", "slug": "hockey", "desc": "Хоккей — командная игра на льду с шайбой.", "events": ["КХЛ: Плей-офф", "ЧМ-2024: Россия — серебро"]},
    {"name": "Волейбол", "slug": "volleyball", "desc": "Волейбол — командная игра через сетку.", "events": ["Лига наций: Россия — бронза"]},
    {"name": "Плавание", "slug": "swimming", "desc": "Плавание — спорт на воде, индивидуальный и командный.", "events": ["Олимпиада: Морозов — золото"]},
    {"name": "Бокс", "slug": "boxing", "desc": "Бокс — контактный вид спорта, бой на ринге.", "events": ["Чемпион мира: Усик", "Бой года: Канело — Головкин"]},
    {"name": "Лёгкая атлетика", "slug": "athletics", "desc": "Лёгкая атлетика — бег, прыжки, метания и др.", "events": ["ЧМ: Прыжки в длину — рекорд"]},
    {"name": "Художественная гимнастика", "slug": "gymnastics", "desc": "Сложнокоординационные упражнения под музыку с предметами: лента, обруч, мяч, булавы.", "events": ["Олимпиада: Сборная России — золото"]},
    {"name": "Биатлон", "slug": "biathlon", "desc": "Биатлон — лыжные гонки и стрельба.", "events": ["Кубок мира: Логинов — победа"]},
    {"name": "Формула-1", "slug": "f1", "desc": "Формула-1 — королевские автогонки.", "events": ["Гран-при Монако: Леклер — победа"]},
    {"name": "Шахматы", "slug": "chess", "desc": "Шахматы — интеллектуальный вид спорта.", "events": ["ЧМ: Непомнящий — серебро"]},
    {"name": "Киберспорт", "slug": "esports", "desc": "Киберспорт — соревнования по видеоиграм.", "events": ["The International: Team Spirit — чемпионы"]},
    {"name": "Рэгби", "slug": "rugby", "desc": "Рэгби — контактная командная игра.", "events": ["ЧМ: Новая Зеландия — золото"]},
    {"name": "Бадминтон", "slug": "badminton", "desc": "Бадминтон — ракеточный вид спорта.", "events": ["ОИ: Китай — золото"]},
    {"name": "Гольф", "slug": "golf", "desc": "Гольф — игра на точность и дальность.", "events": ["Masters: Шеффлер — победа"]},
    {"name": "Сёрфинг", "slug": "surfing", "desc": "Сёрфинг — катание на волнах.", "events": ["ЧМ: Бразилия — золото"]},
    {"name": "Скейтбординг", "slug": "skateboarding", "desc": "Скейтбординг — трюки на доске.", "events": ["ОИ: Япония — золото"]},
    {"name": "Кёрлинг", "slug": "curling", "desc": "Кёрлинг — командная игра на льду.", "events": ["ЧМ: Канада — золото"]},
    {"name": "Фехтование", "slug": "fencing", "desc": "Фехтование — поединки на шпагах.", "events": ["ОИ: Россия — золото"]},
]

@app.route('/', methods=['GET'])
def choose_sport():
    show_all = request.args.get('show_all')
    sports = SPORTS if show_all else SPORTS[:6]
    log_action('view_choose_sport', session.get('username'))
    return render_template('choose_sport.html', sports=SPORTS, header=render_template('header.html', session=session, login_error=request.args.get('login_error')))

@app.route('/sports/<sport_slug>', methods=['GET', 'POST'])
def sport_page(sport_slug):
    sport = next((s for s in SPORTS if s['slug'] == sport_slug), None)
    if not sport:
        return "Вид спорта не найден", 404
    all_comments = load_comments()
    # Фильтруем комментарии по спорту
    comments = [c for c in all_comments if c.get('sport') == sport_slug]
    if request.method == 'POST':
        if 'username' not in session:
            log_action('submit_comment_unauth', None, f'sport: {sport_slug}')
            return redirect(url_for('login'))
        text = request.form.get('text', '').strip()
        if text:
            save_comment({'author': session['username'], 'text': text, 'sport': sport_slug})
            log_action('submit_comment', session['username'], f'sport: {sport_slug}, comment: {text}')
        return redirect(url_for('sport_page', sport_slug=sport_slug))
    # GET-запрос: просто показываем страницу, даже если не авторизован
    log_action('view_sport', session.get('username'), f'sport: {sport_slug}')
    return render_template('sport_page.html', sport=sport, comments=comments, session=session, header=render_template('header.html', session=session, login_error=request.args.get('login_error')))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        users = load_users()
        if username in users:
            error = 'Пользователь уже существует'
            log_action('register_fail_exists', username)
        elif not username or not password:
            error = 'Заполните все поля'
            log_action('register_fail_empty', username)
        else:
            save_user(username, password)
            session['username'] = username
            log_action('register_success', username)
            return redirect(url_for('choose_sport'))  # Исправлено
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    username = session.get('username')
    session.pop('username', None)
    log_action('logout', username)
    return redirect(url_for('choose_sport'))  # Исправлено

# Новый маршрут для входа через шапку
@app.route('/login_in_header', methods=['POST'])
def login_in_header():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if check_user(username, password):
        session['username'] = username
        log_action('login_success', username)
        return redirect(request.referrer or url_for('choose_sport'))
    else:
        log_action('login_fail', username)
        # Передаём ошибку обратно на предыдущую страницу
        return redirect(url_for('choose_sport', login_error='Неверный логин или пароль'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True) 
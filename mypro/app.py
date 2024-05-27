from flask import Flask, render_template, request, redirect, url_for, flash, jsonify ,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# 사용자 모델 정의
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# To-Do 모델 정의
class Todo(db.Model):
    __tablename__ = 'todos'
    todo_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Enum('low', 'medium', 'high'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)


# 시작 페이지 라우트
@app.route('/')
def index():
    return render_template('index.html')


# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.user_id  # 세션에 사용자 ID 저장
            return redirect(url_for('main'))  # 로그인 성공 시 메인 페이지로 이동
        else:
            flash('로그인에 실패했습니다. 사용자 이름 또는 비밀번호를 확인해주세요.', 'error')
    return render_template('index.html')

# 회원가입 페이지
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('index'))
    return render_template('signup.html')

# 아이디 중복 체크
@app.route('/check-username', methods=['POST'])
def check_username():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})
    
    
# 로그인한 사용자의 정보를 얻어오는 함수
def get_current_user():
    # 세션에서 사용자 정보를 가져옴
    user_id = session.get('user_id')
    if user_id is not None:
        # 사용자 ID를 기반으로 사용자 정보를 찾아서 반환
        return User.query.get(user_id)
    else:
        return None
# 메인 페이지 라우트
@app.route('/main')
def main():
    # 현재 로그인한 사용자의 정보를 가져옴
    current_user = get_current_user()
    if current_user is None:
        # 로그인되어 있지 않으면 로그인 페이지로 리다이렉트
        return redirect(url_for('login'))
    
    # 현재 로그인한 사용자의 To-Do 항목만 필터링해서 가져옴
    todos = Todo.query.filter_by(user_id=current_user.user_id).all()
    return render_template('main.html', todos=todos)
# 수정 페이지 라우트
@app.route('/edit_todo/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo_page(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        # 수정 내용을 받아와서 데이터베이스에 반영
        todo.title = request.form['title']
        todo.description = request.form['description']
        todo.priority = request.form['priority']
        todo.due_date = request.form['due_date']
        db.session.commit()
        flash('To-Do 항목이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('main'))
    return render_template('edit_todo.html', todo=todo)

#------리스트 관련 --------
# To-Do 항목 추가
@app.route('/add-todo', methods=['POST'])
def add_todo():
    if request.method == 'POST':
        current_user_id = session.get('user_id')
        if current_user_id:
            title = request.form['title']
            description = request.form['description']
            priority = request.form['priority']
            due_date = request.form['due_date']
            # To-Do 항목을 데이터베이스에 추가
            todo = Todo(user_id=current_user_id, title=title, description=description, priority=priority, due_date=due_date)
            db.session.add(todo)
            db.session.commit()
            flash('To-Do 항목이 추가되었습니다.', 'success')
        else:
            flash('로그인이 필요합니다.', 'error')
    return redirect(url_for('main'))

# To-Do 항목 수정
@app.route('/edit-todo/<int:todo_id>', methods=['POST'])
def edit_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        if request.method == 'POST':
            todo.title = request.form['title']
            todo.description = request.form['description']
            todo.priority = request.form['priority']
            todo.due_date = request.form['due_date']
            db.session.commit()
            flash('To-Do 항목이 수정되었습니다.', 'success')
    else:
        flash('해당 To-Do 항목을 찾을 수 없습니다.', 'error')
    return redirect(url_for('main'))

# To-Do 항목 삭제
@app.route('/delete-todo/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash('To-Do 항목이 삭제되었습니다.', 'success')
    else:
        flash('해당 To-Do 항목을 찾을 수 없습니다.', 'error')
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)

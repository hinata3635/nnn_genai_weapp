from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Optional
from datetime import datetime, timedelta
import os
import random
import string

from io import BytesIO
from langchain.document_loaders import PyPDFLoader
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile
from flask_migrate import Migrate

from flask_wtf import CSRFProtect
from flask_wtf.file import FileField, FileRequired

from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import TextLoader

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.permanent_session_lifetime = timedelta(days=30)

# Flask-Loginの初期化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

# Flask-Migrateの初期化
migrate = Migrate(app, db)

# CSRF保護を有効にする
csrf.init_app(app)

def split_pdf(file_path: str) -> list:
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return pages

def create_answer(user_query, content):
    # .envファイルを読み込む
    load_dotenv()

    # APIキーの登録が必要
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    # テキストを一時ファイルに保存
    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    loader = TextLoader(temp_file_path)

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=100,
        chunk_overlap=0,
        length_function=len,
    )

    index = VectorstoreIndexCreator(
        vectorstore_cls=Chroma,
        embedding=OpenAIEmbeddings(),
        text_splitter=text_splitter,
    ).from_loaders([loader])

    answer = index.query(user_query)

    # 一時ファイルを削除
    os.remove(temp_file_path)

    return answer

def generate_answer(data_content, query):
    # LangChainのロジックをここに移植
    # .envファイルを読み込む
    load_dotenv()

    # APIキーの登録が必要
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    # 一時ファイルとしてdata_contentを保存
    with NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(data_content.encode('utf-8'))
        temp_file_path = temp_file.name

    loader = TextLoader(temp_file_path)
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=100,
        chunk_overlap=0,
        length_function=len,
    )
    index = VectorstoreIndexCreator(
        vectorstore_cls=Chroma,
        embedding=OpenAIEmbeddings(),
        text_splitter=text_splitter,
    ).from_loaders([loader])

    answer = index.query(query)

    # 一時ファイルを削除
    os.remove(temp_file_path)

    return answer

# Userモデルの定義 (UserMixinを継承)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(10), unique=True, nullable=False)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    group_code = db.Column(db.String(8), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_new_user(cls, mail, password, name, group_code):
        unique_id = cls.generate_unique_id()
        existing_user = cls.query.filter_by(mail=mail).first()
        if existing_user is not None:
            return None
        new_user = cls(unique_id=unique_id, mail=mail, name=name, group_code=group_code)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def generate_unique_id(cls, length=10):
        characters = string.ascii_letters + string.digits
        while True:
            unique_id = ''.join(random.choice(characters) for _ in range(length))
            if not cls.query.filter_by(unique_id=unique_id).first():
                return unique_id

# Groupモデルの定義 (UserMixinを継承)
class Group(UserMixin, db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    unique_code = db.Column(db.String(8), unique=True, nullable=False)
    mail = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_new_group(cls, mail, password, name):
        unique_code = cls.generate_unique_code()
        existing_group = cls.query.filter_by(mail=mail).first()
        if existing_group is not None:
            return None
        new_group = cls(unique_code=unique_code, mail=mail, name=name)
        new_group.set_password(password)
        db.session.add(new_group)
        db.session.commit()
        return new_group

    @classmethod
    def generate_unique_code(cls, length=8):
        characters = string.ascii_letters + string.digits
        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(length))
            if not cls.query.filter_by(unique_code=unique_code).first():
                return unique_code

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    user_unique_id = db.Column(db.String(10), db.ForeignKey('users.unique_id'), nullable=False)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    content = db.Column(db.String, nullable=False)
    chat_page_index = db.Column(db.Integer, nullable=False)
    is_user_message = db.Column(db.Boolean, nullable=False)  # 新しいカラムを追加

    def __init__(self, user_unique_id, content, chat_page_index, is_user_message):
        self.user_unique_id = user_unique_id
        self.time_stamp = datetime.utcnow()  # 自動で現在の時刻を設定
        self.content = content
        self.chat_page_index = chat_page_index
        self.is_user_message = is_user_message  # 新しいカラムを初期化

class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    group_unique_id = db.Column(db.String(8), db.ForeignKey('groups.unique_code'), nullable=False)
    file_name = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    data_name = db.Column(db.String(64), nullable=False)

    group = db.relationship('Group', backref=db.backref('data', lazy=True))

    def __init__(self, group_unique_id, file_name, content, data_name):
        self.group_unique_id = group_unique_id
        self.file_name = file_name
        self.content = content
        self.data_name = data_name

class FileUploadForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    data_name = StringField('Data Name', validators=[DataRequired()])
    submit = SubmitField('Upload')

class LogoutForm(FlaskForm):
    pass

# Flask-Login用のユーザーローダー関数
@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type')
    if user_type == 'user':
        return User.query.get(int(user_id))
    elif user_type == 'group':
        return Group.query.get(int(user_id))
    return None

# ログインフォームの定義
class LoginForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# 登録フォームの定義
class RegistrationForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    group_code = StringField('Group Code', validators=[Optional()])
    submit = SubmitField('Register')

# グループログインフォームの定義
class AuthorLoginForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# グループ登録フォームの定義
class AuthorRegistrationForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mail=form.mail.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            session['user_type'] = 'user'
            flash('Login Successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('chachat'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User.create_new_user(
            mail=form.mail.data,
            password=form.password.data,
            name=form.name.data,
            group_code=form.group_code.data if form.group_code.data else ""
        )
        if new_user:
            flash('Registration Successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists. Please choose a different one.', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route('/author_login', methods=['GET', 'POST'])
def author_login():
    form = AuthorLoginForm()
    if form.validate_on_submit():
        group = Group.query.filter_by(mail=form.mail.data).first()
        if group and group.check_password(form.password.data):
            logout_user()  # 既存のUserログイン情報をクリア
            login_user(group, remember=True)
            session['user_type'] = 'group'
            flash('Login Successful!', 'success')
            return redirect(url_for('author_page'))  # author_page にリダイレクト
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('author_login.html', title='Author Login', form=form)

@app.route('/author_page')
@login_required
def author_page():
    form = LogoutForm()
    return render_template('author_page.html', title='Author Page', form=form)

@app.route('/author_register', methods=['GET', 'POST'])
def author_register():
    form = AuthorRegistrationForm()
    if form.validate_on_submit():
        new_group = Group.create_new_group(
            mail=form.mail.data,
            password=form.password.data,
            name=form.name.data
        )
        if new_group:
            flash('Registration Successful! Please log in.', 'success')
            return redirect(url_for('author_login'))
        else:
            flash('Email already exists. Please choose a different one.', 'danger')
    return render_template('author_register.html', title='Author Register', form=form)

@app.route('/chachat')
@login_required
def chachat():
    user_chats = Chat.query.filter_by(user_unique_id=current_user.unique_id).all()
    return render_template('chachat.html', title='chachat_main', chats=user_chats)

@app.route('/file_upload', methods=['GET', 'POST'])
@login_required
def file_upload():
    form = FileUploadForm()
    return render_template('file_upload.html', title='File Upload', form=form)

@app.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)

        # 一時ファイルに保存
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name

        # ファイル内容をテキストに変換
        pages = split_pdf(temp_file_path)
        content = "\n".join([page.page_content for page in pages])

        # 一時ファイルを削除
        os.remove(temp_file_path)

        data_name = request.form['data_name']

        # current_user のクラスに応じて unique_id または unique_code を使用
        if isinstance(current_user, User):
            unique_id = current_user.unique_id
        elif isinstance(current_user, Group):
            unique_id = current_user.unique_code
        else:
            flash('Unknown user type', 'danger')
            return redirect(url_for('file_upload'))

        # 重複データのチェック
        existing_data = Data.query.filter_by(
            group_unique_id=unique_id,
            file_name=filename,
            content=content,
            data_name=data_name
        ).first()

        if existing_data:
            flash('そのファイルはすでに登録されています', 'danger')
            return redirect(url_for('file_upload'))

        new_data = Data(
            group_unique_id=unique_id,
            file_name=filename,
            content=content,
            data_name=data_name
        )
        db.session.add(new_data)
        db.session.commit()
        flash('File successfully uploaded and data saved!', 'success')
        return redirect(url_for('file_upload'))

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)

        # 一時ファイルに保存
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name

        # ファイル内容をテキストに変換
        pages = split_pdf(temp_file_path)
        content = "\n".join([page.page_content for page in pages])

        # 一時ファイルを削除
        os.remove(temp_file_path)

        data_name = request.form['data_name']

        # current_user のクラスに応じて unique_id または unique_code を使用
        if isinstance(current_user, User):
            unique_id = current_user.unique_id
        elif isinstance(current_user, Group):
            unique_id = current_user.unique_code
        else:
            flash('Unknown user type', 'danger')
            return redirect(url_for('file_upload'))

        new_data = Data(
            group_unique_id=unique_id,
            file_name=filename,
            content=content,
            data_name=data_name
        )
        db.session.add(new_data)
        db.session.commit()
        flash('File successfully uploaded and data saved!', 'success')
        return redirect(url_for('file_upload'))

@app.route('/save_chat', methods=['POST'])
@login_required
def save_chat():
    data = request.get_json()
    received_message = data['content']
    is_user_message = data['is_user_message']

    # ユーザーのチャットを保存
    user_chat = Chat(
        user_unique_id=current_user.unique_id,
        content=received_message,
        chat_page_index=0,
        is_user_message=is_user_message
    )
    db.session.add(user_chat)
    db.session.commit()

    # データベースから回答を生成するためのデータを取得
    group_code = current_user.group_code
    group = Group.query.filter_by(id=group_code).first()
    data_entry = Data.query.filter_by(group_unique_id=group.unique_code).first()

    if data_entry:
        data_content = data_entry.content
        print(f"Found data content: {data_entry}")
        try:
            answer = generate_answer(data_content, received_message)
            print(f"Generated answer: {answer}")

            # 生成された回答を保存
            bot_chat = Chat(
                user_unique_id=current_user.unique_id,
                content=answer,
                chat_page_index=0,
                is_user_message=False
            )
            db.session.add(bot_chat)
            db.session.commit()

            return {'status': 'success', 'answer': answer}, 200
        except Exception as e:
            print(f"Error during chat saving or answering: {e}")
            return {'status': 'error', 'message': str(e)}, 500
    else:
        print("No data content found for the group")
        return {'status': 'error', 'message': 'No data content found'}, 404

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if isinstance(current_user, Group):
        logout_user()
        return redirect(url_for('author_login'))
    else:
        logout_user()
        return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=80, debug=False)

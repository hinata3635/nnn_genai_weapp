from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3


app = Flask(__name__)
"""データベースの種類をファイル名を記載"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/git/AI/nnn_genai_weapp/yamada_akira/login/login.db'
"""データベースでイベントシステムがSQLAlchemyのセッションへの変更を追跡するのを無効化（リソースの節約）"""
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
"""SQLAlchemyのインスタンスを作成して変数dbに割り当て"""
db = SQLAlchemy(app)

"""dbのModelを継承したテーブルのクラスを定義"""
class Login(db.Model):
	id = db.Column(db.String(128), primary_key=True)
	password = db.Column(db.String(128), nullable=False)

@app.route('/')
def index():
	data = Login.query.all()
	return render_template('login.html',data=data)

@app.route('/add', methods=['POST'])
def add():
	"""id = request.form['chatbot-text']
	   password = request.form['chatbot-text2']""" 
	id = request.form['id']
	password = request.form['password']
	new_login = Login(id=id,password=password)
	db.session.add(new_login)
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
	id_input = request.args.get('searchId')
	password_input = request.args.get('searchPassword')
	"""
	if id_input is None or len(id_input) == 0:
+         data = Login.query.all()
+   else:
+         data = db.session.query(Login).filter(Login.id.like(id_input)).all()
    return render_template('login.html', data=data)
	"""

if __name__ == '__main__':
	app.run()
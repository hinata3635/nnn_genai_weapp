from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3


app = Flask(__name__)
# データベースの種類をファイル名を記載
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/git/AI/nnn_genai_weapp/yamada_akira/accessDb/todo.db'
#データベースでイベントシステムがSQLAlchemyのセッションへの変更を追跡するのを無効化（リソースの節約）
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#SQLAlchemyのインスタンスを作成して変数dbに割り当て
db = SQLAlchemy(app)

#dbのModelを継承したテーブルのクラスを定義
class ToDo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	todo = db.Column(db.String(128), nullable=False)

@app.route('/')
def index():
	data = ToDo.query.all()
	return render_template('todo.html',data=data)

@app.route('/add', methods=['POST'])
def add():
	todo = request.form['todo']
	id=request.form['id']
	new_todo = ToDo(id=id,todo=todo)
	db.session.add(new_todo)
	db.session.commit()
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run()

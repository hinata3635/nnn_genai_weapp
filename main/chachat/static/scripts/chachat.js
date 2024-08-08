// ユーザーの発言，回答内容を記憶する配列
let userData = [];

// 一番下へ
function chatToBottom() {
	const chatField = document.getElementById('chatbot-body');
	chatField.scroll(0, chatField.scrollHeight - chatField.clientHeight);
}

const userText = document.getElementById('chatbot-text');
const chatSubmitBtn = document.getElementById('chatbot-submit');

// --------------------ロボットの投稿--------------------
function robotOutput(text) {
	// ulとliを作り、左寄せのスタイルを適用し投稿する
	const ul = document.getElementById('chatbot-ul');
	const li = document.createElement('li');
	li.classList.add('left');
	ul.appendChild(li);

	// このdivにテキストを指定
	const div = document.createElement('div');
	li.appendChild(div);
	div.classList.add('chatbot-left');
	div.textContent = text;

	// 一番下までスクロール
	chatToBottom();
}

// --------------------自分の投稿（送信ボタンを押した時の処理）--------------------
// JavaScript内のfetch関数を修正して、CSRFトークンをヘッダーに追加
chatSubmitBtn.addEventListener('click', () => {
	// 空行の場合送信不可
	if (!userText.value || !userText.value.match(/\S/g)) return false;

	// 投稿内容を後に活用するために、配列に保存しておく
	userData.push(userText.value);
	console.log(userData);

	// ulとliを作り、右寄せのスタイルを適用し投稿する
	const ul = document.getElementById('chatbot-ul');
	const li = document.createElement('li');
	// このdivにテキストを指定
	const div = document.createElement('div');

	li.classList.add('right');
	ul.appendChild(li);
	li.appendChild(div);
	div.classList.add('chatbot-right');
	div.textContent = userText.value;

	// チャットデータをサーバーに送信
	fetch('/save_chat', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrfToken
		},
		body: JSON.stringify({
			content: userText.value,
			is_user_message: true  // 自分（User）から送ったメッセージであることを識別
		})
	}).then(response => response.json())
		.then(data => {
			if (data.status === 'success') {
				console.log('チャットが保存されました');
				if (data.answer) {
					// サーバーからの返答を表示
					robotOutput(data.answer);
				}
			} else {
				console.error('チャットの保存に失敗しました');
			}
		}).catch(error => {
			console.error('エラーが発生しました:', error);
		});

	// 一番下までスクロール
	chatToBottom();

	// テキスト入力欄を空白にする
	userText.value = '';
});

// --------------------新しいチャットを作成する機能--------------------
document.getElementById('newChatButton').addEventListener('click', createNewChat);

function createNewChat() {
	// 新しいチャットの要素を作成
	const chatList = document.getElementById('chatList');
	const newChat = document.createElement('div');
	newChat.className = 'chat-item';
	newChat.textContent = '新しいチャット ' + (chatList.children.length + 1);
	chatList.appendChild(newChat);

	// 新しいチャットがクリックされた時のイベントリスナーを追加
	newChat.addEventListener('click', function () {
		openChatWindow(newChat.textContent);
	});

	// クリックされたらチャットウィンドウに内容を表示
	openChatWindow(newChat.textContent);

	// チャット画面を初期化
	initializeChat();
}

function openChatWindow(chatTitle) {
	const chatWindow = document.getElementById('chatWindow');
	chatWindow.style.display = 'block';
	chatWindow.innerHTML = `<h2>${chatTitle}</h2><p>ここにチャットの内容が表示されます。</p>`;
}

function initializeChat() {
	// チャット内容をクリア
	const ul = document.getElementById('chatbot-ul');
	ul.innerHTML = '';

	// ユーザーデータをリセット
	userData = [];

	// 初めからロボットのメッセージを表示
	setTimeout(() => {
		robotOutput('新しいチャットが始まりました');
	}, 100); // 少し遅延を入れて確実に表示されるようにする
}

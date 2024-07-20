// script.js
document.getElementById('newChatButton').addEventListener('click', createNewChat);

function createNewChat() {
    // 新しいチャットの要素を作成
    const chatList = document.getElementById('chatList');
    const newChat = document.createElement('div');
    newChat.className = 'chat-item';
    newChat.textContent = '新しいチャット ' + (chatList.children.length + 1);
    chatList.appendChild(newChat);

    // 新しいチャットがクリックされた時のイベントリスナーを追加
    newChat.addEventListener('click', function() {
        openChatWindow(newChat.textContent);
    });

    // クリックされたらチャットウィンドウに内容を表示
    openChatWindow(newChat.textContent);
}

function openChatWindow(chatTitle) {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.innerHTML = `<h2>${chatTitle}</h2><p>ここにチャットの内容が表示されます。</p>`;
}

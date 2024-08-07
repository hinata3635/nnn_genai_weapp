document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileUpload = document.getElementById('fileUpload');
    const uploadButton = document.getElementById('uploadButton');
    const fileList = document.getElementById('fileList');
    let files = [];

    // ドラッグ＆ドロップイベント
    dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', function (e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // ファイル選択イベント
    fileUpload.addEventListener('change', function () {
        handleFiles(fileUpload.files);
    });

    // ファイルリスト表示
    function handleFiles(selectedFiles) {
        for (let i = 0; i < selectedFiles.length; i++) {
            files.push(selectedFiles[i]);
        }
        renderFileList();
    }

    function renderFileList() {
        fileList.innerHTML = '';
        files.forEach((file, index) => {
            const listItem = document.createElement('div');
            listItem.textContent = file.name;
            const removeButton = document.createElement('button');
            removeButton.textContent = '削除';
            removeButton.addEventListener('click', () => {
                files.splice(index, 1);
                renderFileList();
            });
            listItem.appendChild(removeButton);
            fileList.appendChild(listItem);
        });
    }

    // アップロードボタンのイベント
    uploadButton.addEventListener('click', function () {
        if (files.length === 0) {
            alert('ファイルが選択されていません。');
            return;
        }

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files[]', file);
        });

        // サーバーに送信する場合の例
        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('ファイルがアップロードされました。');
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('ファイルのアップロードに失敗しました。');
        });
    });
});
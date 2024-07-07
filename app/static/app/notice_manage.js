function confirmUnsubscribeAllThreads() {
    if (confirm('すべてのスレッドの更新通知を解除します。本当によろしいですか？')) {
        document.getElementById('unsubscribe_btn').click();
    }
}
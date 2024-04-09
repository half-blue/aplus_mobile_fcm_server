# NOTE THAT THIS IS NOT DJANGO RELATED SCRIPT
# This script is not TREADSAFE
import os
import subprocess
from datetime import datetime, timedelta, timezone
import MySQLdb
from MySQLdb import cursors, connections
import yaml
import logging

# loggingはすべて標準エラー出力になります
logging.basicConfig(level=logging.INFO, format='{asctime} [{levelname}] {name}: {message}', style='{')

# cronで実行する場合、カレントディレクトリを動的に設定する必要がある。
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def load_config() -> dict:
    """機密情報のyamlファイルを読み込み辞書データを返す"""
    with open("batch_config.yaml", "r") as f:
        yaml_dict = yaml.safe_load(f.read())
    return yaml_dict

def mysql_connect(user: str, password: str, host: str, db_name: str, port: int = 3306) -> connections.Connection:
    """MySQLのコネクションを得る"""
    conn = MySQLdb.connect(host=host, port=port,
                           db=db_name, user=user, password=password,
                           charset="utf8mb4")
    return conn

class NoticeMsg:
    def __init__(self, thread_id: int, title: str, body: str, content_type: str, post_id: str, reply_id: str = ""):
        self.thread_id = thread_id
        self.title = title
        self.body = body
        self.content_type = content_type
        assert content_type in ["post", "reply"]
        self.post_id = post_id
        if content_type == "reply":
            self.reply_id = reply_id
        else:
            self.reply_id = ""

def main():
    config = load_config()

    conn = mysql_connect(
        config["MySQL"]["User"],
        config["MySQL"]["Password"],
        config["MySQL"]["Host"],
        config["MySQL"]["Database"],
        config["MySQL"]["Port"]
    )

    RUNTIME = config["Batch"]["Runtime"]
    ABS_PATH = config["Batch"]["AbsolutePath"]

    cur: cursors.Cursor = conn.cursor()

    # タイムスタンプを確認する
    try:
        with open('timestamp.txt', 'r') as f:
            timestamp_str = f.read()
            timestamp_str = timestamp_str.replace('\n', '')
            timestamp = datetime.fromisoformat(timestamp_str)
        # 通知を飛ばしすぎないための安全装置
        if timestamp < (datetime.now(timezone.utc) - timedelta(seconds=300)):
            logging.warning("300秒以内に実行されていません")
            logging.warning("timestamp.txtを更新して終了します")
            cur.close()
            conn.close()
            return
    except:
        logging.warning("timestamp.txtが存在しないかタイムスタンプの読み込みに失敗しました")
        logging.warning("timestamp.txtを作成して終了します")
        cur.close()
        conn.close()
        return
    finally:
        new_timestamp = datetime.now(timezone.utc)
        with open('timestamp.txt', 'w') as f:
            f.write(new_timestamp.isoformat())

    # 通知をすべきスレッドを取得する
    new_posts_and_replies = [] # List[NoticeMsg]
    cur.execute(
        r"""
        SELECT 
            board_post.thread_id,
            board_thread.title,
            board_post.text,
            board_post.post_id
        FROM board_post
        INNER JOIN board_thread ON board_post.thread_id = board_thread.id
        WHERE created_at > %s;
        """,
        [timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')],
    )
    for row in cur.fetchall():
        notice_msg = NoticeMsg(thread_id=row[0], title=row[1], body=row[2], content_type="post", post_id=row[3])
        new_posts_and_replies.append(notice_msg)
    cur.execute(
        r"""
        SELECT
        board_post.thread_id,
        board_thread.title,
        board_reply.text,
        board_post.post_id,
        board_reply.reply_id
        FROM board_reply 
        INNER JOIN board_post ON board_reply.post_id_id = board_post.post_id 
        INNER JOIN board_thread ON board_post.thread_id = board_thread.id
        WHERE board_reply.created_at > %s ;
        """,
        [timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')],
    )
    for row in cur.fetchall():
        notice_msg = NoticeMsg(thread_id=row[0], title=row[1], body=row[2],
                                content_type="reply", post_id=row[3], reply_id=row[4])
        new_posts_and_replies.append(notice_msg)
    
    # 通知を送信する
    for msg in new_posts_and_replies:
        logging.info(f"通知を送信します: thread_id: {msg.thread_id}, type: {msg.content_type}, post_id: {msg.post_id}, reply_id: {msg.reply_id}")
        subprocess.run([RUNTIME, ABS_PATH, "notice", str(msg.thread_id), msg.title, msg.body, msg.content_type, msg.post_id, msg.reply_id])
    if len(new_posts_and_replies) == 0:
        logging.info("通知を送信するスレッドはありませんでした")
    return

if __name__ == "__main__":
    main()
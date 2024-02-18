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
    thread_ids = set()
    cur.execute(
        r"SELECT DISTINCT thread_id FROM board_post WHERE created_at > %s;",
        [timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')],
    )
    for row in cur.fetchall():
        thread_ids.add(row[0])
    cur.execute(
        r"""
        SELECT DISTINCT board_post.thread_id FROM board_reply 
        INNER JOIN board_post ON board_reply.post_id_id = board_post.post_id 
        WHERE board_reply.created_at > %s ;
        """,
        [timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')],
    )
    for row in cur.fetchall():
        thread_ids.add(row[0])
    
    # 通知を送信する
    for tid in thread_ids:
        logging.info("通知を送信します: thread_id = {}".format(tid))
        subprocess.run([RUNTIME, ABS_PATH, "notice", str(tid)])
    if len(thread_ids) == 0:
        logging.info("通知を送信するスレッドはありませんでした")
    return

if __name__ == "__main__":
    main()
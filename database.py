import sqlite3
import json

# SQLite データベースファイルのパス
DB_PATH = "data/tech0_search.db"


# ---------------------------------------------------------
# 1. 初期化：テーブルがなければ作る
# ---------------------------------------------------------
def init_db():
    """pages テーブルを作成する（存在しない場合のみ）"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            url TEXT PRIMARY KEY,
            title TEXT,
            keywords TEXT,
            summary TEXT,
            crawled_at TEXT
        );
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# 2. 新規登録：insert_page()
# ---------------------------------------------------------
def insert_page(url, title, keywords, summary, crawled_at):
    """
    新しいページ情報をデータベースに追加する。

    引数:
        url: ページのURL（主キー）
        title: タイトル
        keywords: キーワード（Pythonリスト）
        summary: 要約
        crawled_at: クロール日時（ISO8601文字列）
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO pages (url, title, keywords, summary, crawled_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            url,
            title,
            json.dumps(keywords, ensure_ascii=False),  # リスト→JSON文字列
            summary,
            crawled_at
        )
    )

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# 3. 取得：get_page_by_url()
# ---------------------------------------------------------
def get_page_by_url(url):
    """
    URL を指定してページ情報を1件取得する。
    見つからなければ None を返す。
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT url, title, keywords, summary, crawled_at FROM pages WHERE url = ?",
        (url,)
    )

    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "url": row[0],
        "title": row[1],
        "keywords": json.loads(row[2]),  # JSON文字列→リスト
        "summary": row[3],
        "crawled_at": row[4]
    }


# ---------------------------------------------------------
# 4. 更新：update_page()
# ---------------------------------------------------------
def update_page(url, title, keywords, summary):
    """
    URL を主キーとしてページ情報を更新する。
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE pages
        SET title = ?, keywords = ?, summary = ?
        WHERE url = ?;
        """,
        (
            title,
            json.dumps(keywords, ensure_ascii=False),
            summary,
            url
        )
    )

    conn.commit()
    conn.close()
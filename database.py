import sqlite3
import json

DB_PATH = "data/tech0_search.db"


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


def insert_page(url, title, keywords, summary, crawled_at):
    """新しいページ情報をデータベースに追加する"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO pages (url, title, keywords, summary, crawled_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            url,
            title,
            json.dumps(keywords, ensure_ascii=False),
            summary,
            crawled_at
        )
    )

    conn.commit()
    conn.close()


def get_page_by_url(url):
    """URL を指定してページ情報を1件取得する"""
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
        "keywords": json.loads(row[2]) if row[2] else [],
        "summary": row[3],
        "crawled_at": row[4]
    }


def update_page(url, title, keywords, summary, crawled_at):
    """ページ情報を更新する"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE pages
        SET title = ?, keywords = ?, summary = ?, crawled_at = ?
        WHERE url = ?;
        """,
        (
            title,
            json.dumps(keywords, ensure_ascii=False),
            summary,
            crawled_at,
            url
        )
    )

    conn.commit()
    conn.close()


def get_all_pages():
    """全ページを取得して検索エンジンに渡せる形にする"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT url, title, keywords, summary, crawled_at FROM pages")
    rows = cur.fetchall()
    conn.close()

    pages = []
    for row in rows:
        pages.append({
            "url": row[0],
            "title": row[1],
            "keywords": json.loads(row[2]) if row[2] else [],
            "summary": row[3],
            "crawled_at": row[4]
        })

    return pages
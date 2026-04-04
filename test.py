import os
import sqlite3
from database import DB_PATH, init_db, insert_page, get_page_by_url

# どのDBを使っているか確認
print("使っているDB:", os.path.abspath(DB_PATH))

# ① DBを初期化（テーブル作成）
init_db()
print("DB初期化完了")

# ② テストデータを挿入
try:
    insert_page(
        url="https://example.com/test",
        title="テストタイトル",
        keywords=["AI", "検索"],
        summary="これはテスト用の要約です。",
        crawled_at="2026-04-04T18:20:00"
    )
    print("insert_page 成功")
except Exception as e:
    print("insert_page エラー:", e)

# ③ get_page_by_url で取得
print("get_page_by_url:", get_page_by_url("https://example.com/test"))

# ④ SQLite を直接叩いて全件確認
print("\n--- SQLite 直接確認 ---")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT * FROM pages")
rows = cur.fetchall()
conn.close()

print("DBの中身:", rows)
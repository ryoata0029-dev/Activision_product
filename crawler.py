"""
crawler.py — Tech0 Search v1.0
Google Docs → GPT → DB → 検索インデックス を一括処理するモジュール
"""

from datetime import datetime

from docs_extractor import GoogleDocsExtractor
from summary import analyze_text
from database import insert_page, update_page, get_page_by_url
from ranking import rebuild_index
from database import get_all_pages


def crawl_and_store(url: str, credentials_path: str = "credentials.json") -> dict:
    """
    Google Docs の URL を受け取り、
    1. 全文取得
    2. GPT で構造化（title / keywords / summary）
    3. DB に保存（新規 or 更新）
    4. 検索インデックスを再構築

    を一括で行う。

    Returns:
        dict: 成功 or エラー内容
    """

    # 1. Google Docs から全文取得
    extractor = GoogleDocsExtractor(credentials_path)
    doc_result = extractor.fetch_text(url)

    if "error" in doc_result:
        return {"error": f"Google Docs 取得エラー: {doc_result['error']}"}

    full_text = doc_result["full_text"]

    # 2. GPT で構造化
    ai_result = analyze_text(full_text)

    if ai_result.get("error"):
        return {"error": f"GPT 解析エラー: {ai_result['error']}"}

    title = ai_result.get("title")
    keywords = ai_result.get("keywords") or []
    summary = ai_result.get("summary")

    # 3. DB に保存（新規 or 更新）
    now = datetime.utcnow().isoformat() + "Z"

    existing = get_page_by_url(url)

    if existing is None:
        insert_page(url, title, keywords, summary, now)
        status = "inserted"
    else:
        update_page(url, title, keywords, summary, now)
        status = "updated"

    # 4. 検索インデックスを再構築
    pages = get_all_pages()
    rebuild_index(pages)

    return {
        "status": status,
        "url": url,
        "title": title,
        "keywords": keywords,
        "summary": summary,
        "crawled_at": now
    }


# 動作テスト
if __name__ == "__main__":
    test_url = input("Google Docs の URL を入力してください: ")
    result = crawl_and_store(test_url)
    print(result)
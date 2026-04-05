import streamlit as st
from crawler import crawl_and_store
from database import (
    load_pages,
    insert_page,
    delete_page,
    get_all_pages,
)
from ranking import get_engine, rebuild_index

st.set_page_config(page_title="Tech0 Search", layout="wide")
st.title("Tech0 Search")

# DB 読み込み
pages = load_pages()

# タブ作成
tab_search, tab_register, tab_list = st.tabs(["検索", "登録", "一覧"])


# -----------------------------
# 🔍 検索タブ（TF-IDF 検索）
# -----------------------------
with tab_search:
    st.header("🔍 資料を検索")

    query = st.text_input("キーワードを入力")

    if st.button("検索する"):
        if not query.strip():
            st.warning("検索ワードを入力してください")
        else:
            # 1. DB から全ページ取得
            pages = get_all_pages()

            # 2. TF-IDF インデックスを再構築
            rebuild_index(pages)

            # 3. 検索実行
            engine = get_engine()
            results = engine.search(query)

            st.subheader(f"検索結果：{len(results)} 件")

            if not results:
                st.info("該当するページはありませんでした。")
            else:
                for p in results:
                    score = p.get("relevance_score", 0)
                    base = p.get("base_score", 0)

                    with st.expander(f"{p['title']}（スコア: {score}）"):
                        st.write(f"**URL:** {p['url']}")
                        st.write(f"**Keywords:** {', '.join(p['keywords'])}")
                        st.write(f"**Summary:** {p['summary']}")
                        st.write(f"**登録日時:** {p['crawled_at']}")
                        st.write(f"**Base Score:** {base}")


# -----------------------------
# 📝 登録タブ（編集して登録）
# -----------------------------
with tab_register:
    st.header("📝 資料を登録")

    url = st.text_input("Google Docs の URL")

    if st.button("解析する"):
        if not url.strip():
            st.warning("URL を入力してください")
        else:
            with st.spinner("解析中..."):
                result = crawl_and_store(url)

            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.edit_data = result
                st.success("解析が完了しました！編集して登録できます。")

    if "edit_data" in st.session_state:
        data = st.session_state.edit_data

        st.subheader("📄 編集して登録")

        title = st.text_input("タイトル", value=data.get("title", ""))
        keywords = st.text_input(
            "キーワード（カンマ区切り）",
            value=",".join(data.get("keywords", []))
        )
        summary = st.text_area("要約", value=data.get("summary", ""), height=200)

        if st.button("登録する"):
            insert_page(
                url=url,
                title=title,
                keywords=[k.strip() for k in keywords.split(",")],
                summary=summary,
                crawled_at=data.get("crawled_at"),
            )

            st.success("登録が完了しました！")
            del st.session_state.edit_data
            st.rerun()


# -----------------------------
# 📄 一覧タブ（削除機能つき）
# -----------------------------
with tab_list:
    st.header("📄 登録済み資料一覧")

    pages = get_all_pages()

    if not pages:
        st.info("まだ登録されたページはありません。")
    else:
        for p in pages:
            with st.expander(p["title"]):
                st.write(f"**URL:** {p['url']}")
                st.write(f"**Keywords:** {', '.join(p['keywords'])}")
                st.write(f"**Summary:** {p['summary']}")
                st.write(f"**登録日時:** {p['crawled_at']}")

                if st.button("🗑️ このページを削除する", key=f"del_{p['url']}"):
                    delete_page(p["url"])
                    st.success("削除しました！")
                    st.rerun()
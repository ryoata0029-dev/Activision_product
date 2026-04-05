import streamlit as st
from crawler import crawl_and_store
from database import get_all_pages, get_page_by_url
from ranking import get_engine, rebuild_index

# ページ設定
st.set_page_config(
    page_title="Tech0 Search v1.0",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Tech0 Search v1.0")

# タブ
tab_search, tab_register, tab_list = st.tabs(["検索", "登録", "一覧"])


# ───────────────────────────────────────────────
# 🔎 1. 検索タブ
# ───────────────────────────────────────────────
with tab_search:
    st.header("🔎 全文検索")

    query = st.text_input("検索ワードを入力してください")

    if st.button("検索する"):
        if not query.strip():
            st.warning("検索ワードを入力してください")
        else:
            engine = get_engine()
            pages = get_all_pages()
            rebuild_index(pages)

            results = engine.search(query)

            st.write(f"検索結果: {len(results)} 件")

            for r in results:
                with st.expander(f"{r['title']}  —  {r['relevance_score']}%"):
                    st.write(f"**URL:** {r['url']}")
                    st.write(f"**キーワード:** {', '.join(r['keywords'])}")
                    st.write(f"**要約:** {r['summary']}")
                    st.write(f"**スコア詳細:** base={r['base_score']}%")


# ───────────────────────────────────────────────
# 📝 2. 登録タブ（Google Docs → GPT → DB）
# ───────────────────────────────────────────────
with tab_register:
    st.header("📝 Google Docs を登録")

    url = st.text_input("Google Docs の URL を入力してください")

    if st.button("登録する"):
        if not url.strip():
            st.warning("URL を入力してください")
        else:
            with st.spinner("クロール中...（Google Docs → GPT → DB）"):
                result = crawl_and_store(url)

            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"登録完了！（{result['status']}）")
                st.write(f"**タイトル:** {result['title']}")
                st.write(f"**キーワード:** {', '.join(result['keywords'])}")
                st.write(f"**要約:** {result['summary']}")


# ───────────────────────────────────────────────
# 📄 3. 一覧タブ（DB 全件表示）
# ───────────────────────────────────────────────
with tab_list:
    st.header("📄 登録済みページ一覧")

    pages = get_all_pages()

    st.write(f"登録件数: {len(pages)} 件")

    for p in pages:
        with st.expander(p["title"]):
            st.write(f"**URL:** {p['url']}")
            st.write(f"**キーワード:** {', '.join(p['keywords'])}")
            st.write(f"**要約:** {p['summary']}")
            st.write(f"**登録日時:** {p['crawled_at']}")
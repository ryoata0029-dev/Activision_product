from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# ▼ .env を読み込む
load_dotenv()

# ▼ APIキーを環境変数から取得
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_text(text: str):
    """
    テキストを入力すると、
    ・資料名（title）
    ・キーワード（keywords）
    ・要約（summary）
    を必ず JSON 形式で返す関数
    """

    prompt = f"""
あなたは文章を構造化して分析するAIです。
以下のテキストを読み、必ず次の3つを JSON 形式で返してください。

- title: 資料名（必須）
- keywords: 重要キーワードを5〜10個（必須）
- summary: 200文字以内の要約（必須）

出力は必ず JSON のみとし、余計な文章は書かないでください。

--- テキスト ---
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは文章を構造化して分析するAIです。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    # ▼ GPT が返した JSON テキストを Python の dict に変換
    result_text = response.choices[0].message.content

    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError:
        # JSON で返らなかった場合の保険（ほぼ起きない）
        result_json = {
            "title": "",
            "keywords": [],
            "summary": ""
        }

    return result_json


# ▼ 動作テスト
if __name__ == "__main__":
    sample_text = """
AIを活用した業務効率化が企業で進んでいる。
特に生成AIは文章作成、要約、検索など幅広い用途で利用されている。
導入企業では生産性向上やコスト削減の効果が報告されている。
"""

    result = analyze_text(sample_text)
    print(result)
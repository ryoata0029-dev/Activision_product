from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_text(text: str):
    """テキストを解析して title / keywords / summary を返す"""

    prompt = f"""
以下のテキストを読み、必ず次の3つを JSON 形式で返してください。

- title: 資料名
- keywords: 重要キーワード（5〜10個）
- summary: 200文字以内の要約

出力は JSON のみ。

--- テキスト ---
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "JSON のみで返してください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    result_text = response.choices[0].message.content

    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "title": None,
            "keywords": None,
            "summary": None,
            "error": "JSON decode failed"
        }

    # keywords が文字列の場合はリストに変換
    if isinstance(result_json.get("keywords"), str):
        result_json["keywords"] = [
            k.strip() for k in result_json["keywords"].split(",") if k.strip()
        ]

    return result_json
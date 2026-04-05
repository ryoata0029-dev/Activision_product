from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_json(text: str):
    """
    GPT の返答から JSON 部分だけを安全に抽出する
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0)
    return None

def analyze_text(text: str):
    """
    GPT を使って title / keywords / summary を生成する（壊れない版）
    """

    prompt = f"""
以下のテキストを読み、必ず次の3つを JSON 形式で返してください。

- title: 資料名
- keywords: 重要キーワード（5〜10個）
- summary: 200文字以内の要約

出力は JSON のみ。文章は書かない。

--- テキスト ---
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "出力は JSON のみで返してください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw = response.choices[0].message.content

    # JSON 部分だけ抽出
    json_text = extract_json(raw)

    if not json_text:
        return {"error": "JSON not found in response"}

    # JSON パース
    try:
        result = json.loads(json_text)
    except json.JSONDecodeError:
        return {"error": "JSON decode failed", "raw": raw}

    # keywords が文字列で返る場合に備えて補正
    if isinstance(result.get("keywords"), str):
        result["keywords"] = [
            k.strip() for k in result["keywords"].split(",") if k.strip()
        ]

    return result
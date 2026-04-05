import re
from typing import Dict, List, Optional, Any
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleDocsExtractor:
    """Google Docs APIを使用してドキュメントのテキストを抽出するクラス"""
    
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

    def __init__(self, credentials_path: str = 'credentials.json'):
        # インスタンス化の時に鍵のパスを設定。後で変更も可能。
        self.credentials_path = credentials_path
        self._service = None

    @property
    def service(self):
        """APIサービスの初期化（通信の使い回しで高速化）"""
        if self._service is None:
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES)
            self._service = build('docs', 'v1', credentials=creds)
        return self._service

    @staticmethod
    def extract_doc_id(url: str) -> Optional[str]:
        """URLからドキュメントIDを正規表現で抽出する"""
        match = re.search(r'/document/d/([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None

    def _extract_text_recursive(self, elements: List[Dict[str, Any]]) -> str:
        """要素リストから再帰的にテキストを抽出（表や目次にも対応）"""
        text_parts = []
        
        for elem in elements:
            # 1. 普通の段落の場合
            if 'paragraph' in elem:
                for element in elem.get('paragraph', {}).get('elements', []):
                    if 'textRun' in element:
                        text_parts.append(element.get('textRun', {}).get('content', ''))
            
            # 2. 表（テーブル）の場合
            elif 'table' in elem:
                for row in elem.get('table', {}).get('tableRows', []):
                    # 内包表記を使ってコードをスッキリさせる
                    row_text = [
                        self._extract_text_recursive(cell.get('content', [])).strip()
                        for cell in row.get('tableCells', [])
                    ]
                    text_parts.append(" | ".join(row_text) + "\n")
                    
            # 3. 目次（Table of Contents）の場合
            elif 'tableOfContents' in elem:
                toc_content = elem.get('tableOfContents', {}).get('content', [])
                text_parts.append(self._extract_text_recursive(toc_content))
                
        # 貯めた文字列のリストを最後に一気に結合（爆速）
        return "".join(text_parts)

    def fetch_text(self, url: str) -> Dict[str, str]:
        """指定されたURLからタイトルと全文を取得する"""
        doc_id = self.extract_doc_id(url)
        if not doc_id:
            return {"error": "無効なURLです。Google DocsのURLを指定してください。"}

        try:
            doc = self.service.documents().get(documentId=doc_id).execute()
            title = doc.get('title', 'No Title')
            content_elements = doc.get('body', {}).get('content', [])
            
            full_text = self._extract_text_recursive(content_elements)
                            
            return {
                "title": title,
                "full_text": full_text.strip()
            }
            
        except HttpError as e:
            return {"error": f"API通信エラー。権限やIDを確認して: {e.reason}"}
        except Exception as e:
            return {"error": f"予期せぬエラー: {str(e)}"}

# === 動作確認用のテストコード ===
if __name__ == "__main__":
    # クラスを実体化（インスタンス化）して使う
    extractor = GoogleDocsExtractor()
    test_url = "https://docs.google.com/document/d/16N__DLcS6es_YK7fnLt9zbB3cABLkSR2wGKYD9bwQoo/edit"
    
    result = extractor.fetch_text(test_url)
    
    if "error" in result:
        print("❌ 失敗:", result["error"])
    else:
        print("✅ 成功！")
        print(f"【タイトル】 {result.get('title')}")
        print(f"【文字数】 {len(result.get('full_text', ''))}文字")
        print("【プレビュー】\n", result.get('full_text', '')[:300])
import re
from typing import Dict, List, Optional, Any
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleDocsExtractor:
    """Google Docs APIを使用してドキュメントのテキストを抽出するクラス"""

    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self._service = None

    @property
    def service(self):
        if self._service is None:
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES)
            self._service = build('docs', 'v1', credentials=creds)
        return self._service

    @staticmethod
    def extract_doc_id(url: str) -> Optional[str]:
        """URLからドキュメントIDを抽出（全パターン対応）"""
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None

    def _extract_text_recursive(self, elements: List[Dict[str, Any]]) -> str:
        text_parts = []

        for elem in elements:
            if 'paragraph' in elem:
                for element in elem.get('paragraph', {}).get('elements', []):
                    if 'textRun' in element:
                        text_parts.append(element.get('textRun', {}).get('content', ''))

            elif 'table' in elem:
                for row in elem.get('table', {}).get('tableRows', []):
                    row_text = [
                        self._extract_text_recursive(cell.get('content', [])).strip()
                        for cell in row.get('tableCells', [])
                    ]
                    text_parts.append(" | ".join(row_text) + "\n")

            elif 'tableOfContents' in elem:
                toc_content = elem.get('tableOfContents', {}).get('content', [])
                text_parts.append(self._extract_text_recursive(toc_content))

        return "".join(text_parts)

    def fetch_text(self, url: str) -> Dict[str, str]:
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

        except FileNotFoundError:
            return {"error": "credentials.json が見つかりません。"}

        except HttpError as e:
            return {"error": f"API通信エラー: {e.reason}"}

        except Exception as e:
            return {"error": f"予期せぬエラー: {str(e)}"}
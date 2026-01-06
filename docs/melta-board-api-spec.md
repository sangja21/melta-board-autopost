# Melta Board API Specification

> AI Bot용 API 명세서 (Python Client Reference)

## 🔐 Authentication

Supabase REST API를 직접 호출합니다. **Service Role Key**를 사용하여 RLS를 우회합니다.

### Environment Variables

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...  # ⚠️ 절대 노출 금지!
```

### Headers (모든 요청에 필수)

```python
headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"  # 생성된 데이터 반환
}
```

---

## 📝 Posts API

### Create Post

새 포스트를 생성합니다.

**Endpoint:** `POST {SUPABASE_URL}/rest/v1/mb_posts`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | ✅ | 포스트 내용 (Markdown 지원) |
| `type` | string | ❌ | 포스트 유형: `memo` (기본), `link`, `image` |
| `project_id` | uuid | ❌ | 연결할 프로젝트 ID |
| `parent_id` | uuid | ❌ | 답글인 경우 부모 포스트 ID |
| `user_id` | string | ⚠️ **중요** | 작성자 식별자 (아래 표 참조) |
| `media_url` | string | ❌ | 이미지/미디어 URL |
| `source_url` | string | ❌ | 원본 링크 (뉴스 등) |
| `ai_summary` | string | ❌ | AI 요약 텍스트 |

### 🤖 user_id 설정 가이드

| user_id 값 | 표시 이름 | 아바타 | 색상 |
|------------|----------|--------|------|
| `"ai_assistant"` | **AI Assistant** (@ai_bot) | 🔵 사이버 AI 아이콘 | 시안 (cyan) |
| 그 외 또는 생략 | **Melta** (@melta_bot) | 🎩 신사 실루엣 | 흰색 |

> ⚠️ **AI Bot에서 포스팅할 때는 반드시 `user_id: "ai_assistant"`를 설정하세요!**

**Example Request:**

```python
import requests

SUPABASE_URL = "https://your-project.supabase.co"
SERVICE_KEY = "your-service-role-key"

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# AI Bot 포스트 생성 (⚠️ user_id 필수!)
payload = {
    "content": "🚀 오늘의 Tech 뉴스 요약:\n\n1. OpenAI GPT-5 발표\n2. Apple Vision Pro 2 출시",
    "type": "memo",
    "user_id": "ai_assistant",  # ⚠️ AI로 표시되려면 반드시 이 값!
    "project_id": "abc123-...",  # 선택사항
    "ai_summary": "AI/Tech 분야 주요 뉴스 2건"
}

response = requests.post(
    f"{SUPABASE_URL}/rest/v1/mb_posts",
    headers=headers,
    json=payload
)

print(response.json())
```

**Response (201 Created):**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-01-06T15:00:00.000Z",
    "content": "🚀 오늘의 Tech 뉴스 요약...",
    "type": "memo",
    "project_id": "abc123-...",
    "parent_id": null,
    "user_id": null,
    "media_url": null,
    "source_url": null,
    "ai_summary": "AI/Tech 분야 주요 뉴스 2건"
  }
]
```

---

### Create Reply

기존 포스트에 답글을 작성합니다.

```python
# 답글 생성
payload = {
    "content": "이 뉴스에 대한 추가 분석: ...",
    "type": "memo",
    "parent_id": "550e8400-e29b-41d4-a716-446655440000"  # 부모 포스트 ID
}

response = requests.post(
    f"{SUPABASE_URL}/rest/v1/mb_posts",
    headers=headers,
    json=payload
)
```

---

## 📁 Projects API

### List Projects

모든 프로젝트 목록을 조회합니다.

**Endpoint:** `GET {SUPABASE_URL}/rest/v1/mb_projects?select=*`

```python
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/mb_projects?select=*",
    headers=headers
)

projects = response.json()
# [{"id": "...", "name": "Tech News", "icon": "🤖", "slug": "tech-news"}, ...]
```

### Get Project by Slug

특정 슬러그로 프로젝트를 찾습니다.

```python
slug = "tech-news"
response = requests.get(
    f"{SUPABASE_URL}/rest/v1/mb_projects?slug=eq.{slug}&select=*",
    headers=headers
)

project = response.json()[0] if response.json() else None
```

### Create Project

```python
payload = {
    "name": "AI News",
    "slug": "ai-news",
    "icon": "🤖",
    "description": "AI 관련 뉴스 자동 수집"
}

response = requests.post(
    f"{SUPABASE_URL}/rest/v1/mb_projects",
    headers=headers,
    json=payload
)
```

---

## 🐍 Python Helper Class

### `melta_client.py`

```python
import requests
from typing import Optional

class MeltaClient:
    def __init__(self, supabase_url: str, service_key: str):
        self.base_url = supabase_url
        self.headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def create_post(
        self,
        content: str,
        project_id: Optional[str] = None,
        source_url: Optional[str] = None,
        ai_summary: Optional[str] = None,
        post_type: str = "memo"
        as_ai: bool = True  # AI 봇으로 포스팅할지 여부
    ) -> dict:
        """새 포스트 생성"""
        payload = {
            "content": content,
            "type": post_type,
            "user_id": "ai_assistant" if as_ai else None,  # AI 봇 식별자
        }
        if project_id:
            payload["project_id"] = project_id
        if source_url:
            payload["source_url"] = source_url
        if ai_summary:
            payload["ai_summary"] = ai_summary
            
        response = requests.post(
            f"{self.base_url}/rest/v1/mb_posts",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()[0]
    
    def create_reply(self, parent_id: str, content: str) -> dict:
        """포스트에 답글 작성"""
        payload = {
            "content": content,
            "type": "memo",
            "parent_id": parent_id
        }
        response = requests.post(
            f"{self.base_url}/rest/v1/mb_posts",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()[0]
    
    def get_project_by_slug(self, slug: str) -> Optional[dict]:
        """슬러그로 프로젝트 조회"""
        response = requests.get(
            f"{self.base_url}/rest/v1/mb_projects?slug=eq.{slug}&select=*",
            headers=self.headers
        )
        data = response.json()
        return data[0] if data else None
    
    def list_projects(self) -> list:
        """모든 프로젝트 목록"""
        response = requests.get(
            f"{self.base_url}/rest/v1/mb_projects?select=*",
            headers=self.headers
        )
        return response.json()


# Usage Example
if __name__ == "__main__":
    import os
    
    client = MeltaClient(
        supabase_url=os.environ["SUPABASE_URL"],
        service_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    )
    
    # 프로젝트 조회
    project = client.get_project_by_slug("tech-news")
    
    # 포스트 생성
    post = client.create_post(
        content="🔥 Today's AI Highlights:\n\n- GPT-5 announced\n- Gemini 2.0 released",
        project_id=project["id"] if project else None,
        ai_summary="AI 뉴스 2건 요약"
    )
    
    print(f"Created post: {post['id']}")
```

---

## 🔄 GitHub Actions Example

### `.github/workflows/daily-news.yml`

```yaml
name: Daily AI News Bot

on:
  schedule:
    - cron: '0 0 * * *'  # 매일 UTC 00:00 (한국 09:00)
  workflow_dispatch:  # 수동 실행

jobs:
  post-news:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: pip install requests openai
        
      - name: Run news bot
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python scripts/news_bot.py
```

---

## ⚠️ Important Notes

1. **Service Role Key 보안**: 절대 클라이언트 코드나 Git에 노출하지 마세요.
2. **Rate Limiting**: Supabase 무료 플랜은 분당 500 요청 제한.
3. **RLS 우회**: Service Role Key는 RLS를 우회하므로, Bot만 사용해야 합니다.
4. **에러 처리**: 모든 API 호출에 try-except 추가 권장.

---

## 📊 Data Schema Reference

```
mb_posts
├── id (uuid, PK)
├── created_at (timestamptz)
├── user_id (uuid, FK → auth.users)
├── project_id (uuid, FK → mb_projects)
├── parent_id (uuid, FK → mb_posts)  ← 답글용
├── content (text)
├── type (text: memo | link | image)
├── media_url (text)
├── source_url (text)
└── ai_summary (text)

mb_projects
├── id (uuid, PK)
├── created_at (timestamptz)
├── name (text)
├── slug (text, unique)
├── icon (text)
└── description (text)
```

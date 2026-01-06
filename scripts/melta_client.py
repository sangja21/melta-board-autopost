import requests
from typing import Optional
import os

class MeltaClient:
    def __init__(self, supabase_url: str, service_key: str):
        self.base_url = supabase_url.strip()
        service_key = service_key.strip()
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
        post_type: str = "memo",
        as_ai: bool = True
    ) -> dict:
        """새 포스트 생성"""
        payload = {
            "content": content,
            "type": post_type,
            "user_id": "ai_assistant" if as_ai else None,
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
        try:
            response.raise_for_status()
            return response.json()[0]
        except Exception as e:
            print(f"Error creating post: {response.text}")
            raise e
    
    def get_project_by_slug(self, slug: str) -> Optional[dict]:
        """슬러그로 프로젝트 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/rest/v1/mb_projects?slug=eq.{slug}&select=*",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None
        except Exception as e:
            print(f"Error fetching project: {e}")
            return None

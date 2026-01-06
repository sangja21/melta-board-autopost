import requests
from typing import Optional
import os

class MeltaClient:
    def __init__(self, supabase_url: str, service_key: str, bot_user_id: Optional[str] = None):
        self.base_url = supabase_url.strip()
        service_key = service_key.strip()
        self.bot_user_id = bot_user_id.strip() if bot_user_id else None
        
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
        
        # Hardcoded Bot User UUID (Must be a valid UUID existing in auth.users)
        # TODO: Replace this with your actual Bot User UUID from Supabase
        bot_uuid = "02b28c0b-0442-493f-b639-668b5774a88f" 
        
        payload = {
            "content": content,
            "type": post_type,
            "user_id": bot_uuid if as_ai else None,
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

    def get_random_post_content(self, project_id: str) -> Optional[str]:
        """특정 프로젝트의 포스트 중 하나를 무작위로 가져옴"""
        import random
        try:
            # 1. Get all IDs first to avoid heavy data transfer
            response = requests.get(
                f"{self.base_url}/rest/v1/mb_posts?project_id=eq.{project_id}&select=id",
                headers=self.headers
            )
            response.raise_for_status()
            posts = response.json()
            
            if not posts:
                return None
                
            # 2. Pick random ID
            random_post = random.choice(posts)
            post_id = random_post['id']
            
            # 3. Fetch content
            detail_response = requests.get(
                f"{self.base_url}/rest/v1/mb_posts?id=eq.{post_id}&select=content",
                headers=self.headers
            )
            detail_response.raise_for_status()
            data = detail_response.json()
            
            return data[0]['content'] if data else None
            
        except Exception as e:
            print(f"Error fetching random post: {e}")
            return None

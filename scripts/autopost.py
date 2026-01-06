import os
import sys
from datetime import datetime
from openai import OpenAI
from melta_client import MeltaClient

# Configuration
OPENAI_MODEL = "gpt-5.2"
TARGET_PROJECT_ID = "fbf63df2-4403-49f6-acd2-fee69ffedbc7"  # Source Project ID

def get_openai_remix(content: str) -> str:
    """Uses OpenAI to remix the content."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""
    You are an AI Bot for Melta Board.
    Your task is to read the following past post and write a "Remix" or "Flashback" post.
    
    Guidelines:
    - Language: Korean (한국어)
    - Tone: Casual, Witty, or Insightful.
    - Context: "과거의 이런 글이 있었네요!", "다시 봐도 흥미로운 주제입니다." 등 재조명하는 느낌.
    - Format: Pure Markdown.

    Past Post Content:
    {content}
    """

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a creative social media editor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    return response.choices[0].message.content.strip()

def process_random_post():
    # Setup Melta Client
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    bot_user_id = os.environ.get("BOT_USER_ID")

    if not supabase_url or not service_key:
        print("Error: Supabase environment variables missing.")
        sys.exit(1)
        
    # Strip whitespace/newlines
    supabase_url = supabase_url.strip()
    service_key = service_key.strip()

    melta = MeltaClient(supabase_url, service_key, bot_user_id)

    print(f"Fetching random post from project {TARGET_PROJECT_ID}...")
    
    # 1. Get Random Post Content
    random_content = melta.get_random_post_content(TARGET_PROJECT_ID)
    
    if not random_content:
        print("No content found in the target project.")
        return

    print("--- Original Content (Snippet) ---")
    print(random_content[:100] + "...")
    print("--------------------------------")

    # 2. Generate Remix via AI
    try:
        if len(random_content.strip()) < 5:
            print("Content too short to remix.")
            return

        remixed_text = get_openai_remix(random_content)
        print("--- Remixed Content ---")
        print(remixed_text)
        print("-----------------------")

        # 3. Post to Supabase (Same Project or General?)
        # User didn't specify destination, so let's put it back in the SAME project for now, or just global.
        # Assuming we post back to the same project to keep it active.
        
        new_post = melta.create_post(
            content=remixed_text,
            project_id=TARGET_PROJECT_ID, # Posting back to the same board
            ai_summary="AI Remix of past content",
            post_type="memo",
            as_ai=True
        )
        print(f"Successfully posted remix. ID: {new_post['id']}")
        
    except Exception as e:
        print(f"Error processing remix: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_random_post()

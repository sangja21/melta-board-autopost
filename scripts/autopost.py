import os
import sys
from datetime import datetime
from openai import OpenAI
from melta_client import MeltaClient

# Configuration
OPENAI_MODEL = "gpt-5.2"
TARGET_PROJECT_ID = "fbf63df2-4403-49f6-acd2-fee69ffedbc7"  # Source Project ID

def load_system_prompt() -> str:
    """Loads the system prompt from prompts/system_prompt.txt."""
    try:
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Warning: Could not load system prompt file: {e}")
        return "You are a helpful AI assistant."

def get_openai_response(content: str) -> str:
    """Uses OpenAI to generate a direct response to the content (treating it as a prompt)."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    system_prompt = load_system_prompt()
    prompt = content
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
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

        response_text = get_openai_response(random_content)
        print("--- AI Response ---")
        print(response_text)
        print("-------------------")

        # 3. Post to Supabase (Same Project)
        
        new_post = melta.create_post(
            content=response_text,
            project_id=TARGET_PROJECT_ID, 
            ai_summary="AI Automatic Response",
            post_type="memo",
            as_ai=True
        )
        print(f"Successfully posted response. ID: {new_post['id']}")
        
    except Exception as e:
        print(f"Error processing remix: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_random_post()

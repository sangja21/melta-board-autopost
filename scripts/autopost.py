import os
import glob
import frontmatter
from datetime import datetime
from openai import OpenAI
from melta_client import MeltaClient
import sys

# Configuration
SOURCES_DIR = "sources"
OPENAI_MODEL = "gpt-5.2"  # Custom model version

def get_openai_summary(content: str) -> str:
    """Uses OpenAI to generate a summary/post from the content."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""
    You are an expert tech editor for 'Melta Board'.
    Read the following raw notes/article and create a engaging Social Media style post (like LinkedIn or Twitter/X thread style but in Markdown).
    
    Guidelines:
    - Tone: Professional, Insightful, yet accessible.
    - Structure: Hook headline, Key takeaways (bullet points), and a concluding thought.
    - Language: Korean (한국어).
    - Length: Under 500 characters if possible, but don't sacrifice clarity.
    - Output format: Pure Markdown.

    Raw Content:
    {content}
    """

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant explaining tech trends."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def process_files():
    # Setup Melta Client
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("Error: Supabase environment variables missing.")
        return

    melta = MeltaClient(supabase_url, service_key)

    # Find md files
    files = glob.glob(os.path.join(SOURCES_DIR, "*.md"))
    
    target_file = None
    post_content = None
    
    # 1. Select a candidate file
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        
        # Skip if already processed
        if post.get("processed"):
            continue
            
        # Found a candidate
        target_file = filepath
        post_content = post
        break
    
    if not target_file:
        print("No new files to process.")
        return

    print(f"Processing file: {target_file}")

    # 2. Generate Content via AI
    try:
        raw_body = post_content.content
        if len(raw_body.strip()) < 10:
            print(f"Skipping {target_file}: Content too short.")
            return

        generated_text = get_openai_summary(raw_body)
        print("--- Generated Content ---")
        print(generated_text)
        print("-------------------------")

        # 3. Post to Supabase
        # Check if project_slug is in frontmatter, else default or None
        project_id = None
        if post_content.get("project_slug"):
            proj = melta.get_project_by_slug(post_content.get("project_slug"))
            if proj:
                project_id = proj["id"]

        new_post = melta.create_post(
            content=generated_text,
            project_id=project_id,
            source_url=post_content.get("source_url"),
            ai_summary="AI Generated from local source",
            post_type="memo",
            as_ai=True
        )
        print(f"Successfully posted to Melta Board. ID: {new_post['id']}")

        # 4. Update File Frontmatter
        post_content["processed"] = True
        post_content["posted_at"] = datetime.now().isoformat()
        post_content["melta_post_id"] = new_post["id"]
        
        # Save back to file
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post_content))
            
        print(f"Updated {target_file} with processed status.")
        
    except Exception as e:
        print(f"Error processing file {target_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_files()

# Melta Board Auto-Post Bot 🤖
> **Personal Feed Autopilot**: AI that keeps your thoughts alive.

이 프로젝트는 **개인 전용 브레인스토밍 파트너(AI Brainstorming Partner)**입니다.  
사용자가 직접 글을 쓰지 않아도, AI가 기존의 생각 파편들을 연결하고 확장하여 **새로운 아이디어와 영감(Inspiration)**을 스스로 게시합니다. 단순한 회상(Remix)을 넘어, 끊임없이 사고를 확장하는 것이 목표입니다.

---

## 🎯 Project Goal

개인 지식보관소나 메모장은 단순한 '창고'가 되기 쉽습니다.  
**Melta Board Auto-Post**는 이 공간을 **'생각의 발전소'**로 바꾸기 위해 다음과 같은 접근 방식을 취합니다:

1.  **Autonomous Ideation**: AI가 스스로 주제를 선정하고 브레인스토밍을 수행하여, 단순한 로그가 아닌 **'생각할 거리'**를 던집니다.
2.  **Continuous Brainstorming**: 과거의 메모는 씨앗(Seed)일 뿐입니다. AI는 이를 바탕으로 **새로운 관점을 제안하고, 꼬리에 꼬리를 무는 질문**을 통해 아이디어를 발전시킵니다.
3.  **Creative Partner**: 봇은 단순 관리자가 아닙니다. 당신의 잠든 아이디어를 깨워 새로운 기획으로 연결해주는 **창의적 파트너**입니다.

## 🛠 Architecture

이 시스템은 **"Random Pick & Ideation"** 전략을 사용합니다.

```mermaid
graph LR
    DB[(Supabase\nProject Data)] -- Random Fetch --> Script[Autopost Script]
    Script -- Seed Content --> AI[OpenAI API\n(Brainstorming Partner)]
    AI -- New Ideas --> Script
    Script -- Create Post --> DB
```

1.  **Fetch (Seed Discovery)**: 타겟 프로젝트의 과거 포스트(아이디어 씨앗) 하나를 무작위로 선정합니다.
2.  **Brainstorming**: AI에게 해당 글을 제공하고, **"Tech Insight가 담긴 파트너"**로서 꼬리에 꼬리를 무는 질문, 반론, 혹은 확장된 아이디어를 생성하게 합니다.
3.  **Post**: 생성된 브레인스토밍 결과를 `AI Assistant` 명의로 게시하여 사용자에게 새로운 영감을 줍니다.

## 📂 Directory Structure

```bash
melta-board-autopost/
├── .github/workflows/ # GitHub Actions 스케줄러 (1시간 주기)
├── docs/              # 개발 문서 및 시스템 아키텍처
├── prompts/           # AI 페르소나 및 시스템 프롬프트 정의
├── scripts/           # 핵심 로직 (Python)
│   ├── autopost.py    # 메인 실행 파일 (Random Pick -> AI -> Post)
│   └── melta_client.py# Supabase 및 외부 API 연동 클라이언트
└── ...
```

## 🚀 Setup & Usage

### 1. Prerequisites
- Python 3.9+
- Supabase Project (Melta Board 호환)
- OpenAI API Key

### 2. Environment Variables (.env)
로컬 실행 시 `.env` 파일이 필요합니다.

```ini
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=ey...
BOT_USER_ID=... (Optional, but usually hardcoded in script)
```

### 3. Running Locally
```bash
# 의존성 설치
pip install -r requirements.txt

# 봇 수동 실행 (1회 Remix 수행)
python scripts/autopost.py
```

### 4. Deployment (GitHub Actions)
리포지토리에 코드를 Push하면 `.github/workflows/hourly_post.yml`에 의해 **매시간 정각**에 자동으로 실행됩니다.
GitHub Repository Settings > Secrets에 위 환경변수들을 등록해야 합니다.

---

## 📝 License
This project is for personal use with Melta Board.

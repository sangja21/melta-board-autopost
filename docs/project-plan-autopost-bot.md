# Project Plan: Melta Board Auto-Post Bot

## 1. Project Goal
GitHub Repository 내의 **Markdown(.md) 파일**들을 소스(Source)로 사용하여, **매 시간(Hourly)** 마다 AI가 내용을 분석/요약 후 Melta Board DB(Supabase)에 자동으로 포스팅하는 시스템 구축.

## 2. Architecture & Workflow

```mermaid
graph TD
    A[GitHub Actions (Cron: Hourly)] --> B(Python Script 실행);
    B --> C{소스 폴더 스캔\n(sources/*.md)};
    C -- "status: ready" --> D[MD 파일 내용 읽기];
    C -- "status: posted" --> E[건너뜀];
    D --> F[AI API 호출\n(OpenAI/Gemini)];
    F -- "요약 및 톤앤매너 정제" --> G[Generated Content];
    G --> H[Supabase API 전송\n(mb_posts 테이블)];
    H -- "Success" --> I[MD 파일 업데이트\n(status: posted)];
    I --> J[Git Commit & Push\n(Bot Account)];
```

### Key Decisions
1.  **Scheduler**: GitHub Actions Cron `0 * * * *` (매 정각 실행).
2.  **State Management (중복 방지)**:
    *   별도의 DB 상태 테이블을 두지 않고, **Source MD 파일의 Frontmatter**를 직접 업데이트하는 방식 사용.
    *   Bot이 포스팅 성공 후, 해당 md 파일 상단에 `processed: true` 또는 `posted_at: 2024-01-01...` 태그를 추가하고 **자동으로 Commit & Push** 함.
3.  **Source Type**: `sources/` 디렉토리 내의 `.md` 파일들.
4.  **AI Model**: 확장성을 위해 `OpenAI` (GPT-4o-mini) 또는 `Google Gemini` 선택 가능하도록 구성 (초기엔 가성비 좋은 모델 권장).

---

## 3. Implementation Steps

### Phase 1: Environment Setup
- [ ] Python 환경 설정 (`requirements.txt`: requests, python-frontmatter, openai 등)
- [ ] GitHub Actions Secrets 설정 (`SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`)
- [ ] Git 권한 설정 (Bot이 리포지토리에 푸시할 수 있도록 권한 부여)

### Phase 2: Python Bot Logic (`scripts/autopost.py`)
1.  **Loader**: `sources/` 폴더의 모든 `.md` 파싱. Frontmatter 확인.
2.  **Filter**: `posted: true`가 **없는** 파일 1개 선택 (한 번에 하나씩 처리 권장).
3.  **Processor (AI)**:
    *   Prompt: "이 글을 읽고 기술 블로그 톤으로 요약하고, 핵심 인사이트 3줄을 뽑아줘."
4.  **Poster**: `MeltaClient` 통해 Supabase Insert (`user_id="ai_assistant"`).
5.  **Updater**: 처리된 파일의 Frontmatter 업데이트 -> Git Commit/Push.

### Phase 3: GitHub Actions Workflow (`.github/workflows/hourly-post.yml`)
- [ ] Cron 스케줄 설정.
- [ ] Python 스크립트 실행 및 Git Auto-Commit 설정.

---

## 4. Potential Risks & Countermeasures

1.  **Git Conflict (충돌)**:
    *   *Risk*: 사용자가 파일을 수정하는 도중 봇이 푸시하면 충돌 가능성.
    *   *Solution*: 봇은 `sources/` 폴더 내의 파일 중 '완료 태그' 부분만 건드림. 하지만 안전을 위해 봇은 **항상 `git pull`을 먼저 수행** 후 작업하도록 스크립트 작성.
2.  **API Failures**:
    *   *Risk*: AI API나 Supabase 다운 시 파일만 업데이트 되면 안 됨.
    *   *Solution*: **"All or Nothing"**. Supabase 전송이 201(Created) 응답을 받은 뒤에만 파일 수정 루틴 진입.
3.  **Empty Queue**:
    *   *Risk*: 포스팅할 새 파일이 없을 때 에러 발생.
    *   *Solution*: "처리할 파일 없음" 로그 남기고 정상 종료 (exit 0).

## 5. Directory Structure Propsal

```bash
.
├── .github/workflows/
│   └── hourly_post.yml
├── docs/
│   └── ...
├── sources/          # [NEW] 사용자가 글감을 던져두는 곳
│   ├── idea-1.md     # 봇이 처리 예정
│   └── idea-2.md     # posted: true (처리됨)
├── scripts/
│   └── autopost.py   # 메인 로직
└── requirements.txt
```

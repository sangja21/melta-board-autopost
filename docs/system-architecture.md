# Melta Board Auto-Post System Architecture

이 문서는 Melta Board용 AI 자동 포스팅 봇의 작동 원리와 내부 로직을 설명합니다.

## 1. System Overview

GitHub Actions를 스케줄러로 활용하여 주기적으로 로컬 Markdown 소스를 스캔하고, AI를 통해 가공하여 Melta Board 서비스에 포스팅하는 자동화 시스템입니다.

```mermaid
graph TD
    Trigger[GitHub Action\n(Every Hour or Push)] --> Runner[Ubuntu Runner]
    Runner --> Script[Running scripts/autopost.py]
    
    subgraph "Logic Flow"
        Script --> Scan{Scan Folder\n/sources/*.md}
        Scan -- Find Unprocessed --> Read[Read MD File]
        Scan -- All Processed --> Exit[Stop with Logs]
        
        Read --> AI[OpenAI API\n(Summarize & Refine)]
        AI --> Post[Supabase API\n(Create Post as AI Bot)]
        
        Post -- Success (201) --> Update[Update Local MD File\n(Add Frontmatter)]
    end
    
    Update --> Git[Git Commit & Push\n(Save State)]
```

---

## 2. Core Logic Workflow

전체 로직은 `scripts/autopost.py`에서 수행되며 다음 4단계로 구성됩니다.

### Step 1: Source Discovery (소스 탐색)
*   **탐색 경로**: `/sources` 디렉토리 내의 모든 `.md` 파일.
*   **필터링 조건**: Frontmatter(문서 상단 메타데이터)에 `processed: true` 키가 **없는** 파일.
*   **처리 정책**: 한 번 실행 시 **단 하나의 파일**만 처리합니다. (순차 처리 및 API 과부하 방지)

### Step 2: AI Content Generation (콘텐츠 생성)
*   **모델**: `gpt-5.2` (설정 가능)
*   **역할(Persona)**: "Tech Insight가 있는 전문 에디터"
*   **입력**: 사용자가 작성한 날것의(Raw) Markdown 노트.
*   **출력**: 제목(Hook), 핵심 요약(Bullet points), 결론이 포함된 소셜 미디어 스타일의 포스팅 텍스트.

### Step 3: Posting to Platform (포스팅)
*   **API**: Supabase REST API 직접 호출 (`mb_posts` 테이블).
*   **작성자**: `user_id`를 `ai_assistant`로 고정하여 AI 봇이 쓴 것으로 표시.
*   **프로젝트 연결**: 소스 파일에 `project_slug`가 명시되어 있다면 해당 프로젝트 ID를 조회하여 자동 매핑.

### Step 4: State Update (상태 동기화)
*   **File Update**: 포스팅 성공 시, 원본 소스 파일을 즉시 수정합니다.
    ```yaml
    ---
    processed: true         # <-- 처리 완료 플래그
    posted_at: 2026-01-06T.. # <-- 처리 시간
    melta_post_id: ...       # <-- 생성된 포스트 ID
    ---
    ```
*   **Git Sync**: 수정된 파일을 `bot` 계정 이름으로 커밋하고 리포지토리에 푸시합니다. 이로써 중복 처리가 영구적으로 방지됩니다.

---

## 3. Directory Structure Role

| 경로 | 역할 | 비고 |
| :--- | :--- | :--- |
| **`sources/`** | 글감 보관소 | 사용자가 아이디어를 `.md`로 던져두는 곳 |
| **`scripts/`** | 로직 스크립트 | `autopost.py`, `melta_client.py` 포함 |
| **`.github/workflows/`** | 스케줄러 | 1시간 주기 Cron 설정 (`hourly_post.yml`) |
| **`requirements.txt`** | 의존성 | Python 패키지 목록 |

## 4. How to Use (User Guide)

1. **글감 추가**: `sources/` 폴더에 새 `.md` 파일을 만듭니다.
    ```markdown
    ---
    project_slug: tech-news  (옵션)
    source_url: https://...  (옵션)
    ---
    # 제목
    내용...
    ```
2. **Push**: GitHub에 푸시합니다.
3. **Wait**: 매 시간 정각(또는 설정에 따라) 봇이 작동하여 포스팅 후, 해당 md 파일에 `processed: true` 태그를 달아줍니다.

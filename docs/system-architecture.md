# Melta Board Auto-Post System Architecture

이 문서는 **Melta Board AI Brainstorming Partner**의 작동 원리와 내부 로직을 설명합니다.

## 1. System Overview

GitHub Actions를 스케줄러로 활용하여 주기적으로 과거의 '생각 씨앗(Post)'을 발굴하고, AI가 이를 바탕으로 새로운 아이디어를 확장하여 Melta Board 서비스에 포스팅하는 자동화 시스템입니다.

```mermaid
graph TD
    Trigger[GitHub Action\n(Every Hour)] --> Runner[Ubuntu Runner]
    Runner --> Script[Running scripts/autopost.py]
    
    subgraph "Brainstorming Logic"
        Script --> Fetch{Random Fetch\n(From Supabase)}
        Fetch -- Get Seed Post --> AI[OpenAI API\n(Brainstorming Partner)]
        Fetch -- No Content --> Exit[Stop]
        
        AI -- Generate Ideas --> Post[Supabase API\n(Create Post as AI Bot)]
    end
    
    Post --> Finish[Log Success]
```

---

## 2. Core Logic Workflow

전체 로직은 `scripts/autopost.py`에서 수행되며 다음 3단계로 구성됩니다.

### Step 1: Seed Discovery (씨앗 발굴)
*   **Target**: 기존 Melta Board 프로젝트(`Target Project ID`)에 저장된 모든 포스트.
*   **Selection**: 수많은 과거의 생각 파편들 중 **하나를 무작위로 선정(Random Pick)**합니다.
*   **Purpose**: 잊혀진 메모나 아이디어를 다시 수면 위로 끌어올려 사고의 확장 재료로 사용합니다.

### Step 2: AI Brainstorming (사고 확장)
*   **Model**: `gpt-5.2` (설정 가능)
*   **Persona**: "Tech Insight가 있는 창의적 파트너 & 에디터"
*   **Input**: 선택된 과거의 포스트(Seed Content).
*   **Output**: 
    1.  **Insight**: 원본 글에 대한 통찰과 분석.
    2.  **Expansion**: 꼬리에 꼬리를 무는 질문 및 새로운 관점 제시.
    3.  **Refinement**: 다듬어진 형태의 소셜 미디어 스타일 텍스트.

### Step 3: Posting (영감 공유)
*   **API**: Supabase REST API 직접 호출 (`mb_posts` 테이블).
*   **Author**: `AI Assistant` (Bot UUID) 명의로 게시.
*   **Type**: 사용자가 새로운 영감을 받을 수 있도록 독립된 포스트로 등록됩니다.

---

## 3. Directory Structure Role

| 경로 | 역할 | 비고 |
| :--- | :--- | :--- |
| **`scripts/`** | 로직 스크립트 | `autopost.py` (Main Logic), `melta_client.py` (API Client) |
| **`.github/workflows/`** | 스케줄러 | 1시간 주기 Cron 설정 (`hourly_post.yml`) |
| **`prompts/`** | AI 설정 | `system_prompt.txt` (AI 페르소나 정의) |
| **`docs/`** | 문서 | 시스템 설계 및 가이드 |
| **`requirements.txt`** | 의존성 | Python 패키지 목록 |

## 4. How to Use

1.  **Configure**: `.env` 및 `scripts/autopost.py` 내의 `TARGET_PROJECT_ID` 설정.
2.  **Deploy**: GitHub에 코드를 푸시하면 스케줄러가 활성화됨.
3.  **Observe**: 매 시간 정각, AI가 당신의 과거 기록을 바탕으로 말을 걸어옵니다.

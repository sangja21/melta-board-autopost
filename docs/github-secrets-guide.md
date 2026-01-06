# GitHub Secrets Configuration Guide

Melta Board Auto-Post 봇이 정상 작동하려면 GitHub Repository Settings에 다음 3가지 Secrets가 반드시 등록되어 있어야 합니다.

## 📍 등록 위치
GitHub Repository > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

## 🔑 필수 Secrets 목록

| Secret Name (대소문자 구분) | 설명 | 예시 값 | 비고 |
| :--- | :--- | :--- | :--- |
| **`SUPABASE_URL`** | Supabase 프로젝트 URL | `https://xxyyzz.supabase.co` | `.env` 파일과 동일 |
| **`SUPABASE_SERVICE_ROLE_KEY`** | 관리자 권한 키 (RLS 우회) | `eyJhbGciOi...` | ⚠️ **anon key가 아님!** 반드시 Service Role Key 사용 |
| **`OPENAI_API_KEY`** | OpenAI API 키 | `sk-proj...` | 잔액이 남아있는지 확인 필요 |

---

### ⚠️ 주의사항
1. **공백 주의**: 값을 복사/붙여넣기 할 때 앞뒤에 공백이 들어가지 않도록 주의하세요.
2. **Key 확인**: Supabase 대시보드 > Project Settings > API 섹션에서 `service_role` 키를 복사해야 합니다. (`anon` 키는 쓰기 권한이 없을 수 있음)

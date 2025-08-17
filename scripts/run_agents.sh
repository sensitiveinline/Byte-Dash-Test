#!/usr/bin/env bash
set -euo pipefail

echo "▶ BYTE-DASH pipeline start"

# 리포 루트로 이동
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

# 출력 폴더 보장
mkdir -p data docs/data

# 1) 데이터 생성: 파이썬 파이프라인 (실패해도 계속 진행)
if python3 -m scripts.pipeline; then
  echo "✔ pipeline.py 완료"
else
  echo "⚠ pipeline.py 실패 또는 없음 — 기존/샘플 데이터 사용"
fi

# 2) data → docs/data 동기화
# rsync 없을 때를 대비해 cp도 백업으로 수행
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete data/ docs/data/
else
  rm -rf docs/data && mkdir -p docs/data
  cp -r data/* docs/data/ 2>/dev/null || true
fi

# 3) 변경이 있을 때만 커밋/푸시
git add docs/data || true
if git diff --cached --quiet; then
  echo "ℹ 변경 없음 (커밋 생략)"
else
  git config user.name  "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git commit -m "chore(data): update docs/data from pipeline"
  git pull --rebase -X ours origin main || true
  git push origin main
  echo "✔ 데이터 커밋/푸시 완료"
fi

echo "✅ BYTE-DASH pipeline done"

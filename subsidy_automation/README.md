# 보조금 관리 자동화 도구

`subsidy_manager.py`는 보조금 사업의 예산/집행/마감일을 CLI로 관리하는 간단한 자동화 프로그램입니다.

## 주요 기능
- 사업 등록 (`add-program`)
- 지출/수입 기록 (`record`)
- 사업별 예산 요약 (`summary`)
- 마감일 리마인더 (`reminders`)

## 사용 예시
```bash
python3 subsidy_automation/subsidy_manager.py add-program "청년 창업 지원" "서울시" 10000000 2026-12-31
python3 subsidy_automation/subsidy_manager.py record "청년 창업 지원" 250000 "홍보비" 2026-02-01 --note "온라인 광고"
python3 subsidy_automation/subsidy_manager.py summary
python3 subsidy_automation/subsidy_manager.py reminders --within-days 60
```

## 데이터 파일
기본적으로 `subsidy_automation/subsidy_db.json`에 저장됩니다.
필요 시 `--db` 옵션으로 경로를 바꿀 수 있습니다.

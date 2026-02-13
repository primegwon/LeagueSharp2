#!/usr/bin/env python3
"""보조금 관리 자동화 CLI.

기능:
- 보조금 사업 등록/조회
- 지출/수입 기록
- 예산 대비 집행률 요약
- 마감일 리마인더 조회
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List


DATE_FMT = "%Y-%m-%d"


@dataclass
class Transaction:
    occurred_on: str
    amount: float
    category: str
    note: str = ""


@dataclass
class SubsidyProgram:
    name: str
    agency: str
    budget: float
    end_date: str
    transactions: List[Transaction] = field(default_factory=list)

    @property
    def total_spent(self) -> float:
        return sum(t.amount for t in self.transactions if t.amount > 0)

    @property
    def remaining_budget(self) -> float:
        return self.budget - self.total_spent

    @property
    def execution_rate(self) -> float:
        if self.budget <= 0:
            return 0.0
        return (self.total_spent / self.budget) * 100


class SubsidyStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.programs: List[SubsidyProgram] = []
        self.load()

    def load(self) -> None:
        if not self.db_path.exists():
            self.programs = []
            return

        raw = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.programs = []
        for item in raw.get("programs", []):
            transactions = [Transaction(**tx) for tx in item.get("transactions", [])]
            self.programs.append(
                SubsidyProgram(
                    name=item["name"],
                    agency=item["agency"],
                    budget=float(item["budget"]),
                    end_date=item["end_date"],
                    transactions=transactions,
                )
            )

    def save(self) -> None:
        payload = {
            "programs": [
                {
                    **asdict(program),
                    "transactions": [asdict(tx) for tx in program.transactions],
                }
                for program in self.programs
            ]
        }
        self.db_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def find_program(self, name: str) -> SubsidyProgram:
        for program in self.programs:
            if program.name == name:
                return program
        raise ValueError(f"'{name}' 사업을 찾을 수 없습니다.")



def validate_date(text: str) -> str:
    try:
        datetime.strptime(text, DATE_FMT)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"날짜 형식은 YYYY-MM-DD 이어야 합니다: {text}"
        ) from exc
    return text



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="보조금 관리 자동화 도구")
    parser.add_argument(
        "--db",
        default="subsidy_automation/subsidy_db.json",
        help="데이터 저장 경로 (기본값: subsidy_automation/subsidy_db.json)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    add_program = sub.add_parser("add-program", help="보조금 사업 추가")
    add_program.add_argument("name", help="사업명")
    add_program.add_argument("agency", help="주관 기관")
    add_program.add_argument("budget", type=float, help="총 예산")
    add_program.add_argument("end_date", type=validate_date, help="사업 종료일 YYYY-MM-DD")

    add_record = sub.add_parser("record", help="지출/수입 기록 추가")
    add_record.add_argument("program", help="사업명")
    add_record.add_argument("amount", type=float, help="금액 (지출은 양수, 환입/수입은 음수)")
    add_record.add_argument("category", help="항목 분류")
    add_record.add_argument("occurred_on", type=validate_date, help="발생일 YYYY-MM-DD")
    add_record.add_argument("--note", default="", help="비고")

    sub.add_parser("summary", help="사업별 예산 요약")

    reminder = sub.add_parser("reminders", help="마감일 리마인더")
    reminder.add_argument(
        "--within-days",
        type=int,
        default=30,
        help="오늘 기준 N일 이내 종료 사업만 출력",
    )

    return parser



def handle_add_program(store: SubsidyStore, args: argparse.Namespace) -> None:
    if any(p.name == args.name for p in store.programs):
        raise ValueError("동일한 사업명이 이미 존재합니다.")

    store.programs.append(
        SubsidyProgram(
            name=args.name,
            agency=args.agency,
            budget=args.budget,
            end_date=args.end_date,
        )
    )
    store.save()
    print(f"✅ 사업 등록 완료: {args.name}")



def handle_record(store: SubsidyStore, args: argparse.Namespace) -> None:
    program = store.find_program(args.program)
    program.transactions.append(
        Transaction(
            occurred_on=args.occurred_on,
            amount=args.amount,
            category=args.category,
            note=args.note,
        )
    )
    store.save()
    print(f"✅ 기록 완료: {args.program} / {args.amount:,.0f}원")



def handle_summary(store: SubsidyStore) -> None:
    if not store.programs:
        print("등록된 사업이 없습니다.")
        return

    print("\n=== 보조금 사업 요약 ===")
    for program in store.programs:
        print(
            f"- {program.name} ({program.agency})\n"
            f"  예산: {program.budget:,.0f}원\n"
            f"  집행: {program.total_spent:,.0f}원\n"
            f"  잔액: {program.remaining_budget:,.0f}원\n"
            f"  집행률: {program.execution_rate:.1f}%\n"
            f"  종료일: {program.end_date}"
        )



def handle_reminders(store: SubsidyStore, within_days: int) -> None:
    today = date.today()
    horizon = today + timedelta(days=within_days)
    upcoming = []

    for program in store.programs:
        end = datetime.strptime(program.end_date, DATE_FMT).date()
        if today <= end <= horizon:
            days_left = (end - today).days
            upcoming.append((days_left, program))

    if not upcoming:
        print(f"향후 {within_days}일 내 종료 예정 사업이 없습니다.")
        return

    print(f"\n=== {within_days}일 내 마감 리마인더 ===")
    for days_left, program in sorted(upcoming, key=lambda x: x[0]):
        print(
            f"- D-{days_left:02d} | {program.name} | 잔액 {program.remaining_budget:,.0f}원 | 종료일 {program.end_date}"
        )



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    store = SubsidyStore(Path(args.db))

    try:
        if args.command == "add-program":
            handle_add_program(store, args)
        elif args.command == "record":
            handle_record(store, args)
        elif args.command == "summary":
            handle_summary(store)
        elif args.command == "reminders":
            handle_reminders(store, args.within_days)
        else:
            parser.print_help()
            return 1
    except ValueError as exc:
        print(f"오류: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

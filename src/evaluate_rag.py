import csv
from pathlib import Path
from datetime import datetime

from rag_chain import load_rag


EVAL_PATH = "data/eval/eval_questions_medi_pick.csv"
RESULT_DIR = "data/eval/results"


def normalize_text(text: str) -> str:
    return (
        str(text)
        .lower()
        .replace(" ", "")
        .replace("\n", "")
        .replace("\t", "")
    )


def split_keywords(keyword_text: str) -> list[str]:
    return [
        keyword.strip()
        for keyword in str(keyword_text).split(";")
        if keyword.strip()
    ]


def keyword_match_score(answer: str, expected_keywords: str) -> tuple[int, int, list[str], list[str]]:
    normalized_answer = normalize_text(answer)
    keywords = split_keywords(expected_keywords)

    matched = []
    missed = []

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)

        if normalized_keyword in normalized_answer:
            matched.append(keyword)
        else:
            missed.append(keyword)

    return len(matched), len(keywords), matched, missed


def judge_pass(
    answer: str,
    expected_keywords: str,
    min_match_ratio: float = 0.5
) -> bool:
    matched_count, total_count, _, _ = keyword_match_score(
        answer,
        expected_keywords
    )

    if total_count == 0:
        return False

    return matched_count / total_count >= min_match_ratio


def summarize_results(rows: list[dict]) -> dict:
    total = len(rows)
    passed = sum(1 for row in rows if row["passed"] == "True")
    failed = total - passed
    accuracy = passed / total * 100 if total else 0

    category_stats = {}

    for row in rows:
        category = row["category"]

        if category not in category_stats:
            category_stats[category] = {
                "total": 0,
                "passed": 0
            }

        category_stats[category]["total"] += 1

        if row["passed"] == "True":
            category_stats[category]["passed"] += 1

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "accuracy": accuracy,
        "category_stats": category_stats
    }


def save_results(rows: list[dict], summary: dict) -> tuple[str, str]:
    Path(RESULT_DIR).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    result_csv_path = f"{RESULT_DIR}/eval_results_{timestamp}.csv"
    summary_txt_path = f"{RESULT_DIR}/eval_summary_{timestamp}.txt"

    fieldnames = [
        "id",
        "category",
        "question",
        "expected_keywords",
        "question_type",
        "matched_keywords",
        "missed_keywords",
        "match_ratio",
        "passed",
        "source_count",
        "answer"
    ]

    with open(result_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write("MediPick RAG 평가 결과\n")
        f.write("=" * 60 + "\n")
        f.write(f"총 문항 수: {summary['total']}\n")
        f.write(f"통과 문항 수: {summary['passed']}\n")
        f.write(f"실패 문항 수: {summary['failed']}\n")
        f.write(f"정답률: {summary['accuracy']:.1f}%\n\n")

        f.write("카테고리별 결과\n")
        f.write("-" * 60 + "\n")

        for category, stat in summary["category_stats"].items():
            total = stat["total"]
            passed = stat["passed"]
            acc = passed / total * 100 if total else 0
            f.write(
                f"{category}: {passed}/{total} "
                f"({acc:.1f}%)\n"
            )

    return result_csv_path, summary_txt_path


def evaluate():
    print("=" * 80)
    print("MediPick RAG 평가 시작")
    print("=" * 80)

    ask = load_rag()
    rows = []

    with open(EVAL_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            question_id = row["id"]
            category = row["category"]
            question = row["question"]
            expected_keywords = row["expected_keywords"]

            print(f"\n[{question_id}] {question}")

            try:
                answer, sources, question_type = ask(question)

                matched_count, total_count, matched, missed = keyword_match_score(
                    answer,
                    expected_keywords
                )

                match_ratio = matched_count / total_count if total_count else 0
                passed = judge_pass(answer, expected_keywords)

                result_row = {
                    "id": question_id,
                    "category": category,
                    "question": question,
                    "expected_keywords": expected_keywords,
                    "question_type": question_type,
                    "matched_keywords": ";".join(matched),
                    "missed_keywords": ";".join(missed),
                    "match_ratio": f"{match_ratio:.2f}",
                    "passed": str(passed),
                    "source_count": len(sources),
                    "answer": answer.replace("\n", " ")
                }

                rows.append(result_row)

                print(f"질문 유형: {question_type}")
                print(f"매칭 키워드: {matched}")
                print(f"누락 키워드: {missed}")
                print(f"통과 여부: {passed}")

            except Exception as e:
                rows.append({
                    "id": question_id,
                    "category": category,
                    "question": question,
                    "expected_keywords": expected_keywords,
                    "question_type": "error",
                    "matched_keywords": "",
                    "missed_keywords": expected_keywords,
                    "match_ratio": "0.00",
                    "passed": "False",
                    "source_count": 0,
                    "answer": str(e)
                })

                print(f"오류 발생: {e}")

    summary = summarize_results(rows)
    result_csv_path, summary_txt_path = save_results(rows, summary)

    print("\n" + "=" * 80)
    print("평가 완료")
    print("=" * 80)
    print(f"총 문항 수: {summary['total']}")
    print(f"통과 문항 수: {summary['passed']}")
    print(f"실패 문항 수: {summary['failed']}")
    print(f"정답률: {summary['accuracy']:.1f}%")

    print("\n카테고리별 결과")
    for category, stat in summary["category_stats"].items():
        total = stat["total"]
        passed = stat["passed"]
        acc = passed / total * 100 if total else 0
        print(f"- {category}: {passed}/{total} ({acc:.1f}%)")

    print("\n저장 파일")
    print(f"- 상세 결과: {result_csv_path}")
    print(f"- 요약 결과: {summary_txt_path}")


if __name__ == "__main__":
    evaluate()
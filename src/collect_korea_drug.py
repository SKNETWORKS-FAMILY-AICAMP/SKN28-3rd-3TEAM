import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.getenv("DRUG_API_KEY")

BASE_URL = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)


def safe_text(element, tag_name):
    target = element.find(tag_name)
    return target.text.strip() if target is not None and target.text else ""


def parse_items(xml_content):
    root = ET.fromstring(xml_content)
    docs = []

    for item in root.findall(".//item"):
        item_name = safe_text(item, "itemName")
        entp_name = safe_text(item, "entpName")
        efcy_qesitm = safe_text(item, "efcyQesitm")
        use_method_qesitm = safe_text(item, "useMethodQesitm")
        atpn_warn_qesitm = safe_text(item, "atpnWarnQesitm")
        atpn_qesitm = safe_text(item, "atpnQesitm")
        intrc_qesitm = safe_text(item, "intrcQesitm")
        se_qesitm = safe_text(item, "seQesitm")
        deposit_method_qesitm = safe_text(item, "depositMethodQesitm")

        if not item_name:
            continue

        content = f"""
의약품명: {item_name}
제조사: {entp_name}

효능:
{efcy_qesitm}

사용법:
{use_method_qesitm}

주의 경고:
{atpn_warn_qesitm}

주의사항:
{atpn_qesitm}

상호작용:
{intrc_qesitm}

부작용:
{se_qesitm}

보관 방법:
{deposit_method_qesitm}
"""

        docs.append({
            "title": item_name,
            "content": content,
            "source": "식품의약품안전처 의약품개요정보 API",
            "url": BASE_URL,
            "metadata": {
                    "manufacturer": entp_name,
                    "type": "drug",
                    "effect": efcy_qesitm,
                    "symptom_text": efcy_qesitm,
                    "usage_text": use_method_qesitm,
                    "warning_text": atpn_qesitm,
                    "interaction_text": intrc_qesitm,
                    "side_effect_text": se_qesitm,
                    "storage_text": deposit_method_qesitm
                }
            })

    return docs


def collect_page(page_no=1, num_of_rows=100):
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "type": "xml"
    }

    response = requests.get(BASE_URL, params=params, timeout=20)

    print(f"[페이지 {page_no}] 상태 코드:", response.status_code)

    if response.status_code != 200:
        print("요청 실패 URL:", response.url)
        print("응답 내용:", response.text[:500])
        return []

    raw_path = f"data/raw/korea_drug_page_{page_no}.xml"

    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    try:
        docs = parse_items(response.content)
    except Exception as e:
        print(f"[페이지 {page_no}] XML 파싱 실패:", e)
        print(response.text[:500])
        return []

    return docs


def collect_all_drugs(target_count=1000, num_of_rows=100, delay=0.3):
    all_docs = []
    seen_titles = set()

    max_pages = (target_count // num_of_rows) + 2

    for page_no in range(1, max_pages + 1):
        docs = collect_page(page_no=page_no, num_of_rows=num_of_rows)

        if not docs:
            print(f"[페이지 {page_no}] 수집된 문서 없음. 종료합니다.")
            break

        for doc in docs:
            title = doc["title"]

            if title not in seen_titles:
                seen_titles.add(title)
                all_docs.append(doc)

        print(f"현재 누적 문서 수: {len(all_docs)}")

        if len(all_docs) >= target_count:
            all_docs = all_docs[:target_count]
            break

        time.sleep(delay)

    save_path = f"data/processed/korea_drug_all_{len(all_docs)}.json"

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"최종 저장 완료: {save_path}")
    print(f"총 수집 문서 수: {len(all_docs)}")
    print("=" * 50)

    return all_docs


if __name__ == "__main__":
    collect_all_drugs(
        target_count=5000,
        num_of_rows=100,
        delay=0.3
    )
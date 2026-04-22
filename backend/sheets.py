import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# 읽을 시트(탭) 목록 — .env의 SHEET_NAMES에 쉼표로 구분해서 입력
# 예: SHEET_NAMES=일피센트(윤곽 양악 리프팅),투비성형외과,브이에이성형외과
SHEET_NAMES_RAW = os.getenv("SHEET_NAMES", "")

# ── 컬럼 인덱스 (A=0, B=1 … G=6 …)
# 실제 스프레드시트 기준:
#   A~F : 확인 필요 (상담일 등 타임라인 컬럼)
#   G   : 수술날
#   H   : 수술부위 (금액 포함)
#   I   : 원장님
#   J   : 말투
#   K   : 게시글 성향
#   L   : 계정 시작날  (hidden 컬럼일 수 있음)
#   M   : 마지막 게시글 (hidden 컬럼일 수 있음)
#   N   : 카페
#   O   : (예비)
#   P   : 닉네임
#   Q   : (예비)
#   R   : 리스트 (글에서 언급할 병원명)
#   S   : 특이사항 (언급금지 등)
#   T   : 비고
#   U   : 이름
#   V   : 년생
#   W   : 추천인
COL = {
    "수술날":       6,   # G
    "수술부위":     7,   # H  (금액 포함)
    "원장님":       8,   # I
    "말투":         9,   # J
    "게시글성향":  10,   # K
    "계정시작일":  11,   # L
    "마지막게시글":12,   # M
    "카페":        13,   # N
    "닉네임":      15,   # P
    "리스트":      17,   # R
    "특이사항":    18,   # S
    "비고":        19,   # T
    "이름":        20,   # U
    "년생":        21,   # V
    "추천인":      22,   # W
}
RANGE_END = "X"   # 읽을 마지막 컬럼


# ── 샘플 데이터 (credentials.json 없을 때 데모용) ──────────────────────
MOCK_PATIENTS = [
    {
        "이름": "김민지",
        "병원명": "일피센트",
        "수술날": "2/18 수술 받음",
        "수술부위": "윤곽 3종 1350만원",
        "원장님": "임종우",
        "말투": "자연스러운 얼굴 라인원함 / 요.... 말이쌈!!",
        "게시글성향": "",
        "리스트": "일피센트, 본디, 얼굴본, 라비앙",
        "특이사항": "원진에서 쌍수·눈교 받음 // 언급 금지",
        "비고": "",
        "년생": "99",
        "추천인": "",
        "카페목록": [
            {"카페": "여우야",  "닉네임": "싸루매",     "계정시작일": "23년도 계정", "마지막게시글": "04월 25일"},
            {"카페": "성위키",  "닉네임": "생각을하자", "계정시작일": "",           "마지막게시글": ""},
            {"카페": "여우야+", "닉네임": "예삐디다",   "계정시작일": "",           "마지막게시글": "라해 가져감"},
            {"카페": "가아사",  "닉네임": "저릿저릿",   "계정시작일": "",           "마지막게시글": ""},
        ],
    },
    {
        "이름": "박수연",
        "병원명": "일피센트",
        "수술날": "11/15 수술 받음",
        "수술부위": "코 재수술 780만원",
        "원장님": "박지훈",
        "말투": "30대 초반 / 자연스럽고 빠른 회복 원함",
        "게시글성향": "",
        "리스트": "일피센트",
        "특이사항": "",
        "비고": "",
        "년생": "93",
        "추천인": "",
        "카페목록": [
            {"카페": "여우야",  "닉네임": "수연이코",   "계정시작일": "22년도 계정", "마지막게시글": "3월 10일"},
            {"카페": "성예사",  "닉네임": "박수연_뷰",  "계정시작일": "",           "마지막게시글": ""},
        ],
    },
    {
        "이름": "이지현",
        "병원명": "투비성형외과",
        "수술날": "3/20 수술 받음",
        "수술부위": "눈 쌍꺼풀 330만원",
        "원장님": "임종우",
        "말투": "20대 초반 / 자연스러움 / ㅠㅠ 이모티콘 많이 씀",
        "게시글성향": "",
        "리스트": "투비",
        "특이사항": "",
        "비고": "",
        "년생": "02",
        "추천인": "",
        "카페목록": [
            {"카페": "여우야", "닉네임": "지현뷰티",   "계정시작일": "24년도 계정", "마지막게시글": "4월 1일"},
            {"카페": "바비",   "닉네임": "j_heye",     "계정시작일": "",           "마지막게시글": ""},
        ],
    },
    {
        "이름": "최유나",
        "병원명": "투비성형외과",
        "수술날": "4/5 수술 받음",
        "수술부위": "지방이식 520만원",
        "원장님": "박지훈",
        "말투": "30대 중반 / 안전·사후관리 중시 / 정중한 ~요 말투",
        "게시글성향": "",
        "리스트": "투비",
        "특이사항": "",
        "비고": "",
        "년생": "91",
        "추천인": "",
        "카페목록": [
            {"카페": "성예사",  "닉네임": "유나리뷰",  "계정시작일": "22년도 계정", "마지막게시글": "4월 18일"},
            {"카페": "강남언니","닉네임": "yna_face",  "계정시작일": "",           "마지막게시글": ""},
        ],
    },
]


def _use_mock() -> bool:
    return not os.path.exists(CREDENTIALS_PATH) or not SPREADSHEET_ID


def _get_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def _get_sheet_names() -> list[str]:
    """env에서 시트명 목록 파싱. 없으면 빈 리스트 (전체 탭 자동 감지)."""
    if SHEET_NAMES_RAW:
        return [s.strip() for s in SHEET_NAMES_RAW.split(",") if s.strip()]
    return []


def _fetch_sheet(service, sheet_name: str) -> list[list]:
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"{sheet_name}!A1:{RANGE_END}")
        .execute()
    )
    return result.get("values", [])


def _auto_detect_sheet_names(service) -> list[str]:
    """SHEET_NAMES 미설정 시, 스프레드시트의 모든 시트 이름 가져오기."""
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    return [s["properties"]["title"] for s in meta.get("sheets", [])]


def _parse_rows(rows: list[list], hospital_name: str) -> list[dict]:
    """
    여러 행을 환자 단위로 묶어 반환.
    - 수술부위(H=7) 또는 원장님(I=8)에 값이 있으면 새 환자 시작
    - 카페(N=13)에 값이 있으면 현재 환자의 카페목록에 추가
    """
    patients = []
    current = None

    for row in rows:
        p = row + [""] * (max(COL.values()) + 2 - len(row))  # 패딩

        surgery_part = p[COL["수술부위"]].strip()
        doctor = p[COL["원장님"]].strip()
        cafe = p[COL["카페"]].strip()

        is_new_patient = bool(surgery_part or doctor)

        if is_new_patient:
            if current:
                patients.append(current)
            current = {
                "이름":        p[COL["이름"]].strip(),
                "병원명":      hospital_name,
                "수술날":      p[COL["수술날"]].strip(),
                "수술부위":    surgery_part,
                "원장님":      doctor,
                "말투":        p[COL["말투"]].strip(),
                "게시글성향":  p[COL["게시글성향"]].strip(),
                "리스트":      p[COL["리스트"]].strip(),
                "특이사항":    p[COL["특이사항"]].strip(),
                "비고":        p[COL["비고"]].strip(),
                "년생":        p[COL["년생"]].strip(),
                "추천인":      p[COL["추천인"]].strip(),
                "카페목록":    [],
            }

        if cafe and current:
            current["카페목록"].append({
                "카페":        cafe,
                "닉네임":      p[COL["닉네임"]].strip(),
                "계정시작일":  p[COL["계정시작일"]].strip(),
                "마지막게시글": p[COL["마지막게시글"]].strip(),
            })

    if current:
        patients.append(current)

    return [p for p in patients if p["이름"] or p["수술부위"]]


def get_patients() -> list[dict]:
    if _use_mock():
        return MOCK_PATIENTS

    service = _get_service()
    sheet_names = _get_sheet_names() or _auto_detect_sheet_names(service)

    all_patients = []
    for sheet_name in sheet_names:
        rows = _fetch_sheet(service, sheet_name)
        all_patients.extend(_parse_rows(rows, hospital_name=sheet_name))
    return all_patients


def get_patient_by_name(name: str) -> dict | None:
    for p in get_patients():
        if p["이름"] == name:
            return p
    return None

import os
from dotenv import load_dotenv

load_dotenv()

# ── 샘플 데이터 (credentials.json 없을 때 데모용) ──────────────────────
MOCK_PATIENTS = [
    {
        "이름": "김민지",
        "닉네임_메모": "",
        "병원알아본날": "11/18",
        "상담날": "12/19",
        "병원방문날": "1/18",
        "수술날": "2/18",
        "수술부위": "윤곽 3종",
        "수술금액": "1,350만원",
        "담당원장": "임종우",
        "연령대말투": "30대 초반",
        "선호키워드": "의견반영,안전,사후관리",
        "말투스타일": "~여 말투",
        "계정시작일": "23년도",
        "마지막게시일": "4월 25일",
        "활동카페": "여우야,성위키,가아사",
        "여우야닉네임": "싸루매",
        "성예사닉네임": "생각을하자",
        "바비닉네임": "저릿저릿",
        "강남언니닉네임": "민지2302",
        "기타닉네임": "",
        "게시이력병원": "A병원,B병원",
        "언급금지사항": "C병원 쌍수·눈교 언급 금지",
        "특이사항": "C병원에서 쌍수·눈교 받은 이력 있음",
    },
    {
        "이름": "박수연",
        "닉네임_메모": "",
        "병원알아본날": "9/5",
        "상담날": "10/12",
        "병원방문날": "11/1",
        "수술날": "11/15",
        "수술부위": "코 재수술",
        "수술금액": "780만원",
        "담당원장": "박지훈",
        "연령대말투": "20대 후반",
        "선호키워드": "자연스러움,회복빠름",
        "말투스타일": "~죠 ~어요 말투",
        "계정시작일": "22년도",
        "마지막게시일": "3월 10일",
        "활동카페": "여우야,성예사",
        "여우야닉네임": "수연이코",
        "성예사닉네임": "박수연_뷰",
        "바비닉네임": "",
        "강남언니닉네임": "suyn_nose",
        "기타닉네임": "",
        "게시이력병원": "B병원",
        "언급금지사항": "",
        "특이사항": "",
    },
]

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# 스프레드시트 컬럼 순서 (실제 시트에 맞게 내일 현장에서 조정)
COLUMNS = [
    "이름",           # A
    "닉네임_메모",     # B  (참고용 내부 메모)
    "병원알아본날",    # C  예: 11/18
    "상담날",         # D  예: 12/19
    "병원방문날",      # E  예: 1/18
    "수술날",         # F  예: 2/18
    "수술부위",       # G  예: 윤곽 3종
    "수술금액",       # H  예: 1350만원
    "담당원장",       # I  예: 임종우
    "연령대말투",     # J  예: 30대초반
    "선호키워드",     # K  예: 의견반영,안전,사후관리
    "말투스타일",     # L  예: ~여 말투
    "계정시작일",     # M  예: 23년도
    "마지막게시일",   # N  예: 4월25일
    "활동카페",       # O  예: 여우야,성위키,가아사
    "여우야닉네임",   # P
    "성예사닉네임",   # Q
    "바비닉네임",     # R
    "강남언니닉네임", # S
    "기타닉네임",     # T  성위키,가아사 등 닉네임 자유기술
    "게시이력병원",   # U  예: A병원,B병원
    "언급금지사항",   # V  예: C병원 쌍수,눈교 언급금지
    "특이사항",       # W  기타 메모
]

PLATFORM_NICKNAME_MAP = {
    "여우야": "여우야닉네임",
    "성예사": "성예사닉네임",
    "바비": "바비닉네임",
    "강남언니": "강남언니닉네임",
}


def _use_mock() -> bool:
    """credentials.json 없거나 SPREADSHEET_ID 미설정이면 샘플 데이터 사용"""
    return not os.path.exists(CREDENTIALS_PATH) or not SPREADSHEET_ID


def _get_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_patients(sheet_name: str = "Sheet1") -> list[dict]:
    if _use_mock():
        return MOCK_PATIENTS
    service = _get_service()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"{sheet_name}!A2:W")
        .execute()
    )
    rows = result.get("values", [])
    patients = []
    for row in rows:
        padded = row + [""] * (len(COLUMNS) - len(row))
        patient = {col: padded[i] for i, col in enumerate(COLUMNS)}
        if patient["이름"]:
            patients.append(patient)
    return patients


def get_patient_by_name(name: str, sheet_name: str = "Sheet1") -> dict | None:
    patients = get_patients(sheet_name)
    for p in patients:
        if p["이름"] == name:
            return p
    return None

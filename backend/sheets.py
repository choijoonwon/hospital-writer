import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
CREDENTIALS_PATH = str(BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))

# 읽을 시트(탭) 목록 — .env의 SHEET_NAMES에 쉼표로 구분해서 입력
# 예: SHEET_NAMES=일피센트(윤곽 양악 리프팅),투비성형외과,브이에이성형외과
SHEET_NAMES_RAW = os.getenv("SHEET_NAMES", "")

# ── 컬럼 인덱스 (A=0, B=1 … 스웨이성형외과 기준 통일)
#   G(6)  : 수술날
#   H(7)  : 수술부위
#   I(8)  : 원장님
#   J(9)  : 컨셉/말투
#   O(14) : 마지막게시글
#   P(15) : 카페
#   Q(16) : 닉네임
#   S(18) : 리스트
#   T(19) : 특이사항
#   U(20) : 비고
#   V(21) : 이름
#   W(22) : 년생
#   X(23) : 추천인
COL = {
    "아이디":        2,   # C
    "수술날":        6,   # G
    "수술부위":      7,   # H
    "원장님":        8,   # I
    "말투":          9,   # J (컨셉/말투)
    "마지막게시글": 14,   # O
    "카페":         15,   # P
    "닉네임":       16,   # Q
    "리스트":       18,   # S
    "특이사항":     19,   # T
    "비고":         20,   # U
    "이름":         21,   # V
    "년생":         22,   # W
    "추천인":       23,   # X
}
RANGE_END = "Y5000"   # 읽을 마지막 컬럼 (행 상한선)

# 헤더 행 자동 감지 기준 키워드 (이 단어가 있는 행 = 헤더)
HEADER_KEY = "수술부위"

# 빨간색 글자 판별 임계값 (red > 0.7, green < 0.4, blue < 0.4)
RED_THRESHOLD = {"red_min": 0.7, "green_max": 0.4, "blue_max": 0.4}


# ── 샘플 데이터 (credentials.json 없을 때 데모용) ──────────────────────
MOCK_PATIENTS = [
    {
        "이름": "김민지",
        "병원명": "일피센트",
        "수술날": "2/18 수술 받음",
        "수술부위": "윤곽 3종 1350만원",
        "원장님": "임종우",
        "말투": "자연스러운 얼굴 라인원함 / 요.... 말이쌈!!",
        "리스트": "일피센트, 본디, 얼굴본, 라비앙",
        "특이사항": "원진에서 쌍수·눈교 받음 // 언급 금지",
        "비고": "",
        "년생": "99",
        "추천인": "",
        "사용불가": False,
        "카페목록": [
            {"카페": "여우야",  "닉네임": "싸루매",     "마지막게시글": "04월 25일"},
            {"카페": "성위키",  "닉네임": "생각을하자", "마지막게시글": ""},
            {"카페": "여우야+", "닉네임": "예삐디다",   "마지막게시글": "라해 가져감"},
            {"카페": "가아사",  "닉네임": "저릿저릿",   "마지막게시글": ""},
        ],
    },
    {
        "이름": "박수연",
        "병원명": "일피센트",
        "수술날": "11/15 수술 받음",
        "수술부위": "코 재수술 780만원",
        "원장님": "박지훈",
        "말투": "30대 초반 / 자연스럽고 빠른 회복 원함",
        "리스트": "일피센트",
        "특이사항": "",
        "비고": "",
        "년생": "93",
        "추천인": "",
        "사용불가": False,
        "카페목록": [
            {"카페": "여우야",  "닉네임": "수연이코",  "마지막게시글": "3월 10일"},
            {"카페": "성예사",  "닉네임": "박수연_뷰", "마지막게시글": ""},
        ],
    },
    {
        "이름": "이지현",
        "병원명": "투비성형외과",
        "수술날": "3/20 수술 받음",
        "수술부위": "눈 쌍꺼풀 330만원",
        "원장님": "임종우",
        "말투": "20대 초반 / 자연스러움 / ㅠㅠ 이모티콘 많이 씀",
        "리스트": "투비",
        "특이사항": "",
        "비고": "",
        "년생": "02",
        "추천인": "",
        "사용불가": False,
        "카페목록": [
            {"카페": "여우야", "닉네임": "지현뷰티", "마지막게시글": "4월 1일"},
            {"카페": "바비",   "닉네임": "j_heye",   "마지막게시글": ""},
        ],
    },
    {
        "이름": "최유나",
        "병원명": "투비성형외과",
        "수술날": "4/5 수술 받음",
        "수술부위": "지방이식 520만원",
        "원장님": "박지훈",
        "말투": "30대 중반 / 안전·사후관리 중시 / 정중한 ~요 말투",
        "리스트": "투비",
        "특이사항": "",
        "비고": "",
        "년생": "91",
        "추천인": "",
        "사용불가": True,
        "카페목록": [
            {"카페": "성예사",  "닉네임": "유나리뷰", "마지막게시글": "4월 18일"},
            {"카페": "강남언니","닉네임": "yna_face", "마지막게시글": ""},
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


def _is_red_color(fg: dict) -> bool:
    """foregroundColor dict을 받아 빨간색 여부 반환."""
    r = fg.get("red", 0)
    g = fg.get("green", 0)
    b = fg.get("blue", 0)
    return (
        r >= RED_THRESHOLD["red_min"]
        and g <= RED_THRESHOLD["green_max"]
        and b <= RED_THRESHOLD["blue_max"]
    )


def _cell_value(cell: dict) -> str:
    """Sheets API rowData cell dict에서 표시 문자열 추출."""
    # formattedValue가 가장 신뢰할 수 있음 (셀에 보이는 그대로)
    if "formattedValue" in cell:
        return cell["formattedValue"]
    ev = cell.get("effectiveValue", {})
    if "stringValue" in ev:
        return ev["stringValue"]
    if "numberValue" in ev:
        return str(ev["numberValue"])
    return ""


def _fetch_sheet(service, sheet_name: str) -> tuple[list[list], set[int]]:
    """
    includeGridData=True로 시트를 읽어 (행 값 목록, 사용불가 행 인덱스 집합) 반환.
    헤더 행(HEADER_KEY 포함) 이후의 데이터 행만 반환하며,
    헤더를 찾지 못하면 ([], set()) 반환 (환자 시트 아님).
    사용불가 판별: 아이디(C열, index 2) 셀의 글자색이 빨간색인 행.
    """
    result = (
        service.spreadsheets()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            ranges=[f"'{sheet_name}'!A1:{RANGE_END}"],
            includeGridData=True,
        )
        .execute()
    )

    sheets_list = result.get("sheets", [])
    if not sheets_list:
        return [], set()

    grid_data = sheets_list[0].get("data", [])
    if not grid_data:
        return [], set()

    all_row_data = grid_data[0].get("rowData", [])
    row_metadata = grid_data[0].get("rowMetadata", [])

    # 각 rowData를 (값 리스트, 셀 목록) 으로 변환 — 숨긴 행은 건너뜀
    all_rows_values = []
    all_rows_cells = []
    for i, row_dict in enumerate(all_row_data):
        # hiddenByUser=True인 행 스킵
        meta = row_metadata[i] if i < len(row_metadata) else {}
        if meta.get("hiddenByUser"):
            continue
        cells = row_dict.get("values", [])
        values = [_cell_value(c) for c in cells]
        all_rows_values.append(values)
        all_rows_cells.append(cells)

    # 헤더 행 자동 감지
    header_idx = None
    for i, row in enumerate(all_rows_values):
        if any(HEADER_KEY in str(v) for v in row):
            header_idx = i
            break

    if header_idx is None:
        return [], set()

    data_rows_values = all_rows_values[header_idx + 1:]
    data_rows_cells = all_rows_cells[header_idx + 1:]

    # 아이디(C열 = index 2) 글자색이 빨간색인 행 인덱스 수집
    aidi_col = COL["아이디"]
    red_set: set[int] = set()
    for i, cells in enumerate(data_rows_cells):
        if len(cells) > aidi_col:
            cell = cells[aidi_col]
            # userEnteredFormat 우선, effectiveFormat 차선
            fmt = cell.get("userEnteredFormat", cell.get("effectiveFormat", {}))
            text_fmt = fmt.get("textFormat", {})
            # foregroundColorStyle.rgbColor 도 확인 (테마 색상 미적용 시)
            fg = text_fmt.get("foregroundColorStyle", {}).get("rgbColor") \
                 or text_fmt.get("foregroundColor", {})
            if fg and _is_red_color(fg):
                red_set.add(i)

    return data_rows_values, red_set


def _auto_detect_sheet_names(service) -> list[str]:
    """SHEET_NAMES 미설정 시, 스프레드시트의 모든 시트 이름 가져오기."""
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    return [s["properties"]["title"] for s in meta.get("sheets", [])]


def _parse_rows(rows: list[list], hospital_name: str, red_set: set[int] | None = None) -> list[dict]:
    """
    여러 행을 환자 단위로 묶어 반환.
    - 수술부위(H=7) 또는 원장님(I=8)에 값이 있으면 새 환자 시작
    - 카페(P=15)에 값이 있으면 현재 환자의 카페목록에 추가
    - red_set: 아이디 셀이 빨간색인 행 인덱스 집합 → 사용불가 계정
    """
    if red_set is None:
        red_set = set()

    patients = []
    current: dict | None = None

    for row_idx, row in enumerate(rows):
        p = row + [""] * (max(COL.values()) + 2 - len(row))  # 패딩

        surgery_part = p[COL["수술부위"]].strip()
        doctor = p[COL["원장님"]].strip()
        cafe = p[COL["카페"]].strip()
        disabled = row_idx in red_set  # 빨간 글자 = 사용불가

        is_new_patient = bool(surgery_part or doctor)

        if is_new_patient:
            if current:
                patients.append(current)
            # 이름 없으면 아이디로 대체
            name = p[COL["이름"]].strip() or p[COL["아이디"]].strip()
            current = {
                "이름":        name,
                "사용불가":    disabled,
                "병원명":      hospital_name,
                "수술날":      p[COL["수술날"]].strip(),
                "수술부위":    surgery_part,
                "원장님":      doctor,
                "말투":        p[COL["말투"]].strip(),
                "리스트":      p[COL["리스트"]].strip(),
                "특이사항":    p[COL["특이사항"]].strip(),
                "비고":        p[COL["비고"]].strip(),
                "년생":        p[COL["년생"]].strip(),
                "추천인":      p[COL["추천인"]].strip(),
                "카페목록":    [],
            }

        if cafe and current:
            current["카페목록"].append({
                "카페":         cafe,
                "닉네임":       p[COL["닉네임"]].strip(),
                "마지막게시글": p[COL["마지막게시글"]].strip(),
            })

    if current:
        patients.append(current)

    return [p for p in patients if p["이름"] or p["수술부위"]]


# ── 인메모리 캐시 ──────────────────────────────────────────────
_cache: list[dict] | None = None


def _load_from_sheets() -> list[dict]:
    service = _get_service()
    sheet_names = _get_sheet_names() or _auto_detect_sheet_names(service)
    all_patients = []
    for sheet_name in sheet_names:
        rows, red_set = _fetch_sheet(service, sheet_name)
        all_patients.extend(_parse_rows(rows, hospital_name=sheet_name, red_set=red_set))
    return all_patients


def get_patients(force_refresh: bool = False) -> list[dict]:
    global _cache
    if _use_mock():
        return MOCK_PATIENTS
    if _cache is None or force_refresh:
        _cache = _load_from_sheets()
    return _cache


def refresh_cache() -> list[dict]:
    """캐시를 강제로 새로 고침하고 결과를 반환."""
    return get_patients(force_refresh=True)


def get_patient_by_name(name: str) -> dict | None:
    for p in get_patients():
        if p["이름"] == name:
            return p
    return None

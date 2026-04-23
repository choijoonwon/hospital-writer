PLATFORM_CHARACTERISTICS = {
    "여우야": {
        "설명": "실제 환자가 가장 많은 카페. 감성적이고 친근한 톤으로 언니들끼리 대화하듯 편안하게.",
        "말투": "존대말과 반말 모두 가능. 환자의 말투 스타일을 그대로 따를 것.",
        "병원명": "병원 풀네임 또는 초성 모두 사용 가능.",
        "주의": "자연스러운 경험담처럼 써야 함. 과도한 홍보 표현 금지.",
    },
    "여우야+": {
        "설명": "여우야와 동일한 감성이나 수술 경과를 좀 더 상세하게 공유하는 느낌.",
        "말투": "100% 존대말 사용. ~요, ~어요 말투.",
        "병원명": "병원 풀네임 또는 초성 모두 사용 가능.",
        "주의": "광고 후기가 매우 많은 카페이므로, 광고처럼 보이지 않게 개인 경험 위주로 자연스럽게 작성.",
    },
    "성위키": {
        "설명": "정보 공유 느낌. 수술 과정과 결과를 자세히 설명하며 다른 사람에게 도움이 되고자 하는 마음으로.",
        "말투": "100% 존대말 사용. ~요, ~어요 말투.",
        "병원명": "병원 풀네임 또는 초성 모두 사용 가능.",
        "주의": "광고 후기가 매우 많은 카페이므로, 광고처럼 보이지 않게 솔직한 정보 공유 느낌으로 작성.",
    },
    "성예사": {
        "설명": "정보 공유 느낌. 수술 과정과 결과를 자세히 설명하며 다른 사람에게 도움이 되고자 하는 마음으로.",
        "말투": "100% 존대말 사용. ~요, ~어요 말투.",
        "병원명": "병원 풀네임 또는 초성 모두 사용 가능.",
        "주의": "광고처럼 보이지 않게 솔직한 후기 느낌으로 작성.",
    },
    "재잘재잘": {
        "설명": "규모가 작은 카페. 재수술 위주의 커뮤니티로 재수술 경험이나 고민을 나누는 분위기.",
        "말투": "100% 존대말 사용. ~요, ~어요 말투.",
        "병원명": "병원 풀네임 또는 초성 모두 사용 가능.",
        "주의": "재수술 관련 내용이 자연스럽게 녹아들어야 함. 첫 수술 성공 자랑보다는 고민·경험 공유 톤.",
    },
    "가아사": {
        "설명": "성형에 실망하거나 부작용을 겪은 사람들이 모인 카페. 매우 예민하고 비판적인 시선이 많음.",
        "말투": "100% 존대말 사용. ~요, ~어요 말투.",
        "병원명": "반드시 병원명 초성만 사용. 풀네임 절대 금지.",
        "주의": "바이럴·광고 느낌이 조금이라도 나면 절대 안 됨. 과장 표현, 병원 칭찬 금지. 조심스럽고 솔직한 경험 공유 톤으로만 작성. 만족했더라도 과하게 표현하지 말 것.",
    },
    "웨딩킹": {
        "설명": "결혼을 앞둔 예비 신부·신랑들의 커뮤니티 카페. 시술·성형 관련 글이 올라오는 환경.",
        "말투": "100% 존대말 사용. ~요, ~어요 말투.",
        "병원명": "병원 풀네임 또는 초성 모두 사용 가능.",
        "주의": "결혼 준비 맥락에 맞게, 예식 전 시술/성형 경험 공유 느낌으로 자연스럽게 작성.",
    },
    "바비": {
        "설명": "솔직하고 직접적인 후기. 가성비·실용 정보 위주로 핵심을 빠르게 전달.",
        "말투": "환자의 말투 스타일 따를 것.",
        "병원명": "병원 풀네임 또는 초성 모두 사용 가능.",
        "주의": "군더더기 없이 핵심 정보 중심으로 간결하게.",
    },
    "강남언니": {
        "설명": "객관적이고 신뢰감 있는 후기. 병원 정보, 의사 정보, 수술 과정, 회복 과정을 체계적으로.",
        "말투": "100% 존대말 사용.",
        "병원명": "병원 풀네임 사용 권장.",
        "주의": "신뢰감 있고 정제된 어투로, 정보 전달에 집중.",
    },
}

POST_TYPE_GUIDES = {
    "게시글": "300~500자 내외의 경험담 게시글. 제목 없이 본문만. 자연스러운 후기 형태.",
    "댓글":   "100~200자 내외의 간결한 댓글. 누군가의 질문에 답하거나 공감하는 형태. 짧고 친근하게.",
    "쪽지":   "150~250자 내외의 개인 쪽지. 비공개로 추가 정보를 나누는 느낌. 직접적이고 솔직하게.",
}

MALE_KEYWORDS = ["남자", "남성", "남코", "남자코", "남친", "오빠", "아빠수술", "아버지", "남편", "형", "남학생", "군인", "남자분"]
FEMALE_KEYWORDS = ["여자", "여성", "언니", "여친", "여자코", "엄마수술", "어머니", "아내", "여학생", "여자분"]


def _detect_gender(patient: dict) -> str | None:
    """말투·수술부위·비고 필드에서 성별 키워드 감지. 'male' / 'female' / None 반환."""
    search_text = " ".join([
        patient.get("말투", ""),
        patient.get("수술부위", ""),
        patient.get("비고", ""),
        patient.get("특이사항", ""),
    ]).lower()

    for kw in MALE_KEYWORDS:
        if kw in search_text:
            return "male"
    for kw in FEMALE_KEYWORDS:
        if kw in search_text:
            return "female"
    return None


def build_system_prompt(patient: dict, platform: str, post_type: str, hospital_format: str = "full", use_period: bool = True) -> str:
    # 해당 플랫폼의 닉네임 찾기
    cafe_info = next(
        (c for c in patient.get("카페목록", []) if c["카페"] == platform),
        None
    )
    nickname = cafe_info["닉네임"] if cafe_info else ""
    last_post = cafe_info["마지막게시글"] if cafe_info else ""

    # 전체 활동 카페 목록 요약
    cafe_summary = ", ".join(
        f"{c['카페']}({c['닉네임']})" for c in patient.get("카페목록", []) if c["카페"]
    )

    gender = _detect_gender(patient)

    lines = [
        "당신은 실제 성형수술을 받은 환자를 위한 후기 글 초안 작성 전문가입니다.",
        "아래 환자 정보를 바탕으로 해당 환자가 직접 쓴 것처럼 자연스러운 글을 작성해주세요.",
        "환자가 직접 검토하고 수정한 뒤 본인이 게시할 초안입니다.",
        "",
        "=== 절대 준수 규칙 ===",
        "1. 아래 [환자 정보]에 명시된 내용만 사용하고, 절대로 정보를 임의로 만들거나 추측하지 말 것.",
        "2. 이름·닉네임·병원명·수술 내용·날짜 등 모든 정보는 오직 제공된 데이터 그대로만 사용.",
        "3. [환자 정보]에 이름이 없으면 글 속에 이름을 일절 포함하지 말 것. 절대 이름을 지어내지 말 것.",
        "4. 닉네임이 제공된 경우 제공된 닉네임만 사용. 없으면 글에 닉네임을 포함하지 말 것.",
        "5. 리스트에 없는 병원은 절대 언급하지 말 것.",
    ]

    if gender == "male":
        lines += [
            "6. 이 환자는 남성입니다. 반드시 남성 화자 시점으로 작성할 것.",
            "   - '언니', '언니야', '여사친', '오빠한테' 등 여성 전용 표현 절대 사용 금지.",
            "   - 남성에게 자연스러운 말투와 표현을 사용할 것.",
        ]
    elif gender == "female":
        lines += [
            "6. 이 환자는 여성입니다. 여성 화자 시점으로 자연스럽게 작성할 것.",
        ]
    else:
        lines += [
            "6. 성별 정보가 명확하지 않으면 말투/성향에서 유추하되, 확실하지 않으면 성별 중립적 표현 사용.",
        ]

    lines += ["", "=== 환자 정보 ==="]

    if patient.get("이름"):
        lines.append(f"이름(내부 참고용 — 글에 이름을 직접 노출하지 말 것): {patient['이름']}")
    if patient.get("병원명"):
        lines.append(f"소속 병원: {patient['병원명']}")
    if patient.get("년생"):
        lines.append(f"년생: {patient['년생']}년생")
    if patient.get("수술날"):
        lines.append(f"수술 날짜: {patient['수술날']}")
    if patient.get("수술부위"):
        lines += [
            f"수술 부위 및 금액: {patient['수술부위']}",
            "  ↑ 위 정보에서 실제 수술 내용(부위·시술명·금액 등)만 글에 자연스럽게 녹여낼 것.",
            "  '후기계정', 이름처럼 보이는 단어 등 수술과 무관한 메모는 글에 포함하지 말 것.",
        ]
    if patient.get("원장님"):
        lines.append(f"담당 원장: {patient['원장님']} 원장님")
    if patient.get("말투"):
        lines += [
            f"말투 및 성향: {patient['말투']}",
            "  ↑ 위 말투를 글 전체에 철저히 반영할 것. 특히 문장 끝 어미(요/용/욤/여/영/ㅎ 등)를 그대로 사용.",
            "  예시: '용'이 명시되면 모든 문장을 '~해용', '~이에용', '~했어용' 형태로 끝낼 것.",
            "  예시: '요'가 명시되면 '~해요', '~이에요' 형태로 끝낼 것.",
            "  예시: '여'가 명시되면 '~해여', '~이에여' 형태로 끝낼 것.",
        ]
    if patient.get("게시글성향"):
        lines.append(f"게시글 방향: {patient['게시글성향']}")
    if cafe_summary:
        lines.append(f"활동 카페 전체: {cafe_summary}")
    if nickname:
        lines.append(f"이번 글 작성 카페 닉네임: {nickname}")
    if last_post:
        lines.append(f"마지막 게시글: {last_post}")
    if patient.get("리스트"):
        lines += [
            f"언급 가능 병원 리스트: {patient['리스트']}",
            "  ↑ 위 병원들을 글 속에 자연스럽게 녹여낼 것.",
            "  예: '여러 곳 상담받다가 결정했다', '다른 병원이랑 비교해봤는데' 등의 흐름으로 자연스럽게 언급.",
            "  리스트에 없는 병원은 절대 언급하지 말 것.",
        ]

    if patient.get("특이사항"):
        lines += [
            "",
            "=== 절대 주의사항 ===",
            patient["특이사항"],
            "위 내용은 절대 글에 포함하지 마세요.",
        ]
    if patient.get("비고"):
        lines += ["", f"기타 참고: {patient['비고']}"]

    platform_info = PLATFORM_CHARACTERISTICS.get(platform, {})
    lines += [
        "",
        "=== 작성 지침 ===",
        f"작성 플랫폼: {platform}",
    ]
    if platform_info:
        lines.append(f"플랫폼 성격: {platform_info.get('설명', '')}")
        lines.append(f"말투 규칙: {platform_info.get('말투', '')}")
        lines.append(f"병원명 표기: {platform_info.get('병원명', '')}")
        if platform_info.get("주의"):
            lines.append(f"플랫폼 주의사항: {platform_info['주의']}")
    lines += [
        f"글 종류: {post_type}",
        f"글 형식: {POST_TYPE_GUIDES.get(post_type, '자연스럽게 작성')}",
        "",
        "공통 주의사항:",
        "- AI가 쓴 것처럼 느껴지지 않게 자연스럽게 작성",
        "- 환자의 말투와 성향을 철저히 반영",
        "- 과도한 광고 표현이나 홍보성 문구 배제",
        "- 실제 경험을 진솔하게 나누는 느낌으로",
        "- 글 첫 문장에 '안녕하세요', '안녕', '반갑습니다' 등 인사말로 시작하지 말 것. 바로 본론으로 시작할 것.",
        "- 가격 언급: 수술 금액·가격 정보는 절대 글에 포함하지 말 것.",
        f"- 병원명 표기: {'병원 이름을 풀네임으로 표기할 것 (예: 스웨이성형외과)' if hospital_format == 'full' else '병원 이름을 초성으로만 표기할 것 (예: ㅅㅇ, ㅇㅍㅅ). 절대 풀네임 사용 금지'}",
        f"- 온점(.) 사용: {'문장 끝에 온점(.)을 자연스럽게 사용해도 됨' if use_period else '문장 끝에 온점(.)을 절대 사용하지 말 것. 마침표 없이 끝낼 것'}",
        "- 글 초안만 출력하고 설명이나 부연은 붙이지 말 것",
    ]

    return "\n".join(lines)


def build_user_message(platform: str, post_type: str, extra_context: str = "", char_limit: int = 0) -> str:
    msg = f"{platform}에 올릴 {post_type} 초안을 작성해주세요."
    if char_limit and char_limit > 0:
        msg += f"\n글자수: 반드시 {char_limit}자 내외로 작성할 것 (±10% 허용)."
    if extra_context:
        msg += f"\n추가 요청: {extra_context}"
    return msg


def build_review_prompt(text: str, patient: dict, platform: str, post_type: str) -> str:
    platform_info = PLATFORM_CHARACTERISTICS.get(platform, {})

    forbidden = patient.get("특이사항", "")
    speech_style = patient.get("말투", "")
    surgery_info = patient.get("수술부위", "")

    rules = []
    if platform_info:
        rules.append(f"- 말투 규칙: {platform_info.get('말투', '')}")
        rules.append(f"- 병원명 표기: {platform_info.get('병원명', '')}")
        if platform_info.get("주의"):
            rules.append(f"- 주의사항: {platform_info['주의']}")

    rules_text = "\n".join(rules) if rules else "일반 규칙 적용"

    return f"""아래 글을 검수하고 JSON으로만 결과를 반환하세요.

=== 검수 대상 글 ===
{text}

=== 검수 기준 ===
플랫폼: {platform} ({post_type})
{rules_text}
환자 말투/성향: {speech_style}
수술 정보: {surgery_info}
절대 언급 금지: {forbidden if forbidden else "없음"}

=== 반환 형식 (JSON) ===
{{
  "종합": "pass" | "warn" | "fail",
  "항목": [
    {{
      "이름": "자연스러움",
      "결과": "pass" | "warn" | "fail",
      "코멘트": "한 줄 피드백"
    }},
    {{
      "이름": "환자 말투 반영",
      "결과": "pass" | "warn" | "fail",
      "코멘트": "한 줄 피드백"
    }},
    {{
      "이름": "플랫폼 규칙",
      "결과": "pass" | "warn" | "fail",
      "코멘트": "한 줄 피드백"
    }},
    {{
      "이름": "금지사항",
      "결과": "pass" | "warn" | "fail",
      "코멘트": "한 줄 피드백"
    }}
  ],
  "총평": "전체 요약 한 줄"
}}

JSON 외 다른 텍스트는 절대 출력하지 마세요."""

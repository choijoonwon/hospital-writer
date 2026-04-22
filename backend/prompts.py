PLATFORM_CHARACTERISTICS = {
    "여우야":   "감성적이고 친근한 톤. 언니들끼리 대화하듯 편안하게. 개인적인 감정과 경험 위주로 서술.",
    "여우야+":  "여우야와 동일한 감성. 약간 더 상세하게 수술 경과를 공유하는 느낌.",
    "성위키":   "정보 공유 느낌. 수술 과정과 결과를 자세히 설명. 다른 사람들에게 도움이 되고자 하는 마음으로.",
    "성예사":   "정보 공유 느낌. 수술 과정과 결과를 자세히 설명. 다른 사람들에게 도움이 되고자 하는 마음으로.",
    "가아사":   "솔직하고 직접적인 후기. 가격 대비 만족도, 실용적인 정보 위주. 핵심을 빠르게 전달.",
    "바비":     "솔직하고 직접적인 후기. 가성비, 실용 정보 위주. 핵심을 빠르게 전달.",
    "강남언니": "객관적이고 신뢰감 있는 후기. 병원 정보, 의사 정보, 수술 과정, 회복 과정을 체계적으로.",
}

POST_TYPE_GUIDES = {
    "게시글": "300~500자 내외의 경험담 게시글. 제목 없이 본문만. 자연스러운 후기 형태.",
    "댓글":   "100~200자 내외의 간결한 댓글. 누군가의 질문에 답하거나 공감하는 형태. 짧고 친근하게.",
    "쪽지":   "150~250자 내외의 개인 쪽지. 비공개로 추가 정보를 나누는 느낌. 직접적이고 솔직하게.",
}


def build_system_prompt(patient: dict, platform: str, post_type: str) -> str:
    # 해당 플랫폼의 닉네임 찾기
    cafe_info = next(
        (c for c in patient.get("카페목록", []) if c["카페"] == platform),
        None
    )
    nickname = cafe_info["닉네임"] if cafe_info else ""
    last_post = cafe_info["마지막게시글"] if cafe_info else ""
    account_start = cafe_info["계정시작일"] if cafe_info else ""

    # 전체 활동 카페 목록 요약
    cafe_summary = ", ".join(
        f"{c['카페']}({c['닉네임']})" for c in patient.get("카페목록", []) if c["카페"]
    )

    lines = [
        "당신은 실제 성형수술을 받은 환자를 위한 후기 글 초안 작성 전문가입니다.",
        "아래 환자 정보를 바탕으로 해당 환자가 직접 쓴 것처럼 자연스러운 글을 작성해주세요.",
        "환자가 직접 검토하고 수정한 뒤 본인이 게시할 초안입니다.",
        "",
        "=== 환자 정보 ===",
    ]

    if patient.get("이름"):
        lines.append(f"이름(내부용): {patient['이름']}")
    if patient.get("병원명"):
        lines.append(f"소속 병원: {patient['병원명']}")
    if patient.get("년생"):
        lines.append(f"년생: {patient['년생']}년생")
    if patient.get("수술날"):
        lines.append(f"수술 날짜: {patient['수술날']}")
    if patient.get("수술부위"):
        lines.append(f"수술 부위 및 금액: {patient['수술부위']}")
    if patient.get("원장님"):
        lines.append(f"담당 원장: {patient['원장님']} 원장님")
    if patient.get("말투"):
        lines.append(f"말투 및 성향: {patient['말투']}")
    if patient.get("게시글성향"):
        lines.append(f"게시글 방향: {patient['게시글성향']}")
    if cafe_summary:
        lines.append(f"활동 카페 전체: {cafe_summary}")
    if nickname:
        lines.append(f"이번 글 작성 카페 닉네임: {nickname}")
    if account_start:
        lines.append(f"해당 계정 시작일: {account_start}")
    if last_post:
        lines.append(f"마지막 게시글: {last_post}")
    if patient.get("리스트"):
        lines.append(f"글에서 언급 가능한 병원/자연스럽게 녹여낼 곳: {patient['리스트']}")

    if patient.get("특이사항"):
        lines += [
            "",
            "=== 절대 주의사항 ===",
            patient["특이사항"],
            "위 내용은 절대 글에 포함하지 마세요.",
        ]
    if patient.get("비고"):
        lines += ["", f"기타 참고: {patient['비고']}"]

    lines += [
        "",
        "=== 작성 지침 ===",
        f"작성 플랫폼: {platform}",
        f"플랫폼 특성: {PLATFORM_CHARACTERISTICS.get(platform, '자연스럽게 작성')}",
        f"글 종류: {post_type}",
        f"글 형식: {POST_TYPE_GUIDES.get(post_type, '자연스럽게 작성')}",
        "",
        "주의사항:",
        "- AI가 쓴 것처럼 느껴지지 않게 자연스럽게 작성",
        "- 환자의 말투와 성향을 철저히 반영",
        "- 과도한 광고 표현이나 홍보성 문구 배제",
        "- 실제 경험을 진솔하게 나누는 느낌으로",
        "- 글 초안만 출력하고 설명이나 부연은 붙이지 말 것",
    ]

    return "\n".join(lines)


def build_user_message(platform: str, post_type: str, extra_context: str = "") -> str:
    msg = f"{platform}에 올릴 {post_type} 초안을 작성해주세요."
    if extra_context:
        msg += f"\n추가 요청: {extra_context}"
    return msg

PLATFORM_CHARACTERISTICS = {
    "여우야": "감성적이고 친근한 톤. 언니들끼리 대화하듯 편안하게. 개인적인 감정과 경험 위주로 서술.",
    "성예사": "정보 공유 느낌. 수술 과정과 결과를 자세히 설명. 다른 사람들에게 도움이 되고자 하는 마음으로.",
    "바비": "솔직하고 직접적인 후기. 가격 대비 만족도, 실용적인 정보 위주. 핵심을 빠르게 전달.",
    "강남언니": "객관적이고 신뢰감 있는 후기. 병원 정보, 의사 정보, 수술 과정, 회복 과정을 체계적으로. 사진 설명 포함 가능.",
}

POST_TYPE_GUIDES = {
    "게시글": "300~500자 내외의 경험담 게시글. 제목 없이 본문만. 자연스러운 후기 형태.",
    "댓글": "100~200자 내외의 간결한 댓글. 누군가의 질문에 답하거나 공감하는 형태. 짧고 친근하게.",
    "쪽지": "150~250자 내외의 개인 쪽지. 비공개로 추가 정보를 나누는 느낌. 직접적이고 솔직하게.",
}


def build_system_prompt(patient: dict, platform: str, post_type: str) -> str:
    nickname = patient.get(f"{platform}닉네임", "") or patient.get("닉네임_메모", "")

    lines = [
        "당신은 실제 성형수술을 받은 환자를 위한 후기 글 초안 작성 전문가입니다.",
        "아래 환자 정보를 바탕으로 해당 환자가 직접 쓴 것처럼 자연스러운 글을 작성해주세요.",
        "환자가 직접 검토하고 수정한 뒤 본인이 게시할 초안입니다.",
        "",
        "=== 환자 정보 ===",
    ]

    if patient.get("이름"):
        lines.append(f"이름(내부용): {patient['이름']}")
    if nickname:
        lines.append(f"해당 플랫폼 닉네임: {nickname}")
    if patient.get("병원알아본날"):
        lines.append(f"병원 알아본 시기: {patient['병원알아본날']}")
    if patient.get("상담날"):
        lines.append(f"상담 받은 날: {patient['상담날']}")
    if patient.get("병원방문날"):
        lines.append(f"병원 방문한 날: {patient['병원방문날']}")
    if patient.get("수술날"):
        lines.append(f"수술 받은 날: {patient['수술날']}")
    if patient.get("수술부위"):
        lines.append(f"수술 부위: {patient['수술부위']}")
    if patient.get("수술금액"):
        lines.append(f"수술 금액: {patient['수술금액']}")
    if patient.get("담당원장"):
        lines.append(f"담당 원장: {patient['담당원장']} 원장님")
    if patient.get("연령대말투"):
        lines.append(f"연령대/말투: {patient['연령대말투']}")
    if patient.get("말투스타일"):
        lines.append(f"말투 스타일: {patient['말투스타일']}")
    if patient.get("선호키워드"):
        lines.append(f"중요하게 생각하는 것: {patient['선호키워드']}")
    if patient.get("계정시작일"):
        lines.append(f"계정 시작 시기: {patient['계정시작일']}")
    if patient.get("마지막게시일"):
        lines.append(f"마지막 게시글 날짜: {patient['마지막게시일']}")
    if patient.get("활동카페"):
        lines.append(f"주로 활동하는 카페: {patient['활동카페']}")
    if patient.get("게시이력병원"):
        lines.append(f"이전에 글 올린 병원: {patient['게시이력병원']}")

    if patient.get("언급금지사항"):
        lines.append("")
        lines.append("=== 절대 언급 금지 ===")
        lines.append(patient["언급금지사항"])
        lines.append("위 내용은 절대 글에 포함하지 마세요.")

    if patient.get("특이사항"):
        lines.append("")
        lines.append(f"참고 사항: {patient['특이사항']}")

    lines += [
        "",
        "=== 작성 지침 ===",
        f"플랫폼: {platform}",
        f"플랫폼 특성: {PLATFORM_CHARACTERISTICS.get(platform, '자연스럽게 작성')}",
        f"글 종류: {post_type}",
        f"글 형식 가이드: {POST_TYPE_GUIDES.get(post_type, '자연스럽게 작성')}",
        "",
        "주의사항:",
        "- AI가 쓴 것처럼 느껴지지 않게 자연스럽게 작성",
        "- 환자의 말투와 스타일을 철저히 반영",
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

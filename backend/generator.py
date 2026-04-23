import os
import json
from dotenv import load_dotenv
from backend.prompts import build_system_prompt, build_user_message, build_review_prompt

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "claude").lower()


def generate_post(patient: dict, platform: str, post_type: str, extra_context: str = "", char_limit: int = 0, hospital_format: str = "full", use_period: bool = True) -> str:
    system_prompt = build_system_prompt(patient, platform, post_type, hospital_format, use_period)
    user_message = build_user_message(platform, post_type, extra_context, char_limit)

    if AI_PROVIDER == "openai":
        return _call_openai(system_prompt, user_message, model="gpt-4o", max_tokens=1500)
    return _call_claude(system_prompt, user_message, model="claude-sonnet-4-6", max_tokens=1500)


def review_post(text: str, patient: dict, platform: str, post_type: str) -> dict:
    system_prompt = "당신은 SNS 마케팅 글 검수 전문가입니다. 반드시 JSON만 출력하세요. 다른 텍스트는 절대 포함하지 마세요."
    user_message = build_review_prompt(text, patient, platform, post_type)

    try:
        if AI_PROVIDER == "openai":
            raw = _call_openai(system_prompt, user_message, model="gpt-4o-mini", max_tokens=800)
        else:
            raw = _call_claude(system_prompt, user_message, model="claude-haiku-4-5-20251001", max_tokens=800)

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception:
        return {"error": True}


def _call_claude(system_prompt: str, user_message: str, model: str, max_tokens: int) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def _call_openai(system_prompt: str, user_message: str, model: str, max_tokens: int) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

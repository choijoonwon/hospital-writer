import os
from dotenv import load_dotenv
from backend.prompts import build_system_prompt, build_user_message

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "claude").lower()


def generate_post(patient: dict, platform: str, post_type: str, extra_context: str = "") -> str:
    system_prompt = build_system_prompt(patient, platform, post_type)
    user_message = build_user_message(platform, post_type, extra_context)

    if AI_PROVIDER == "openai":
        return _generate_openai(system_prompt, user_message)
    return _generate_claude(system_prompt, user_message)


def _generate_claude(system_prompt: str, user_message: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def _generate_openai(system_prompt: str, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content

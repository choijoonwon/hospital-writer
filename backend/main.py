import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="병원 마케팅 글쓰기 자동화")

PLATFORMS = ["여우야", "여우야+", "성위키", "성예사", "재잘재잘", "가아사", "웨딩킹", "바비", "강남언니"]
POST_TYPES = ["게시글", "댓글", "쪽지"]


class GenerateRequest(BaseModel):
    patient_name: str
    platform: str
    post_type: str
    extra_context: str = ""
    char_limit: int = 0
    hospital_format: str = "full"
    use_period: bool = True  # False면 문장 끝 온점 사용 안 함


@app.get("/api/patients")
def list_patients():
    try:
        from backend.sheets import get_patients
        patients = get_patients()
        return {"patients": [
            {
                "이름": p["이름"],
                "사용불가": p.get("사용불가", False),
                "병원명": p.get("병원명", ""),
                "수술부위": p.get("수술부위", ""),
                "수술날": p.get("수술날", ""),
                "원장님": p.get("원장님", ""),
                "말투": p.get("말투", ""),
                "리스트": p.get("리스트", ""),
                "특이사항": p.get("특이사항", ""),
                "비고": p.get("비고", ""),
                "년생": p.get("년생", ""),
                "추천인": p.get("추천인", ""),
                "카페목록": [c.get("닉네임", "") + " " + c.get("카페", "") for c in p.get("카페목록", [])],
            }
            for p in patients
        ]}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="credentials.json 파일이 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hospitals")
def list_hospitals():
    try:
        from backend.sheets import get_patients
        patients = get_patients()
        hospitals = sorted({p.get("병원명", "") for p in patients if p.get("병원명")})
        return {"hospitals": hospitals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patients/{name}")
def get_patient(name: str):
    try:
        from backend.sheets import get_patient_by_name
        patient = get_patient_by_name(name)
        if not patient:
            raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다.")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
def generate(req: GenerateRequest):
    if req.post_type not in POST_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 글 종류: {req.post_type}")

    try:
        from backend.sheets import get_patient_by_name
        patient = get_patient_by_name(req.patient_name)
        if not patient:
            raise HTTPException(status_code=404, detail="환자를 찾을 수 없습니다.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시트 읽기 오류: {e}")

    try:
        from backend.generator import generate_post, review_post
        text = generate_post(patient, req.platform, req.post_type, req.extra_context, req.char_limit, req.hospital_format, req.use_period)
        review = review_post(text, patient, req.platform, req.post_type)
        return {"result": text, "review": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 생성 오류: {e}")


@app.post("/api/patients/refresh")
def refresh_patients():
    try:
        from backend.sheets import refresh_cache
        patients = refresh_cache()
        return {"count": len(patients), "message": "새로고침 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
def get_config():
    return {
        "platforms": PLATFORMS,
        "post_types": POST_TYPES,
        "ai_provider": os.getenv("AI_PROVIDER", "claude"),
        "sheets_configured": bool(os.getenv("SPREADSHEET_ID")),
    }


app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend")

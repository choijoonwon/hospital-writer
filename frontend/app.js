const API = "";

let selectedPlatform = "";
let selectedPostType = "";

async function loadConfig() {
  try {
    const res = await fetch(`${API}/api/config`);
    const cfg = await res.json();
    const badge = document.getElementById("status-badge");
    if (cfg.sheets_configured) {
      badge.textContent = `AI: ${cfg.ai_provider === "claude" ? "Claude" : "GPT-4o"} · Sheets 연결됨`;
      badge.className = "badge badge-ok";
    } else {
      badge.textContent = "⚠ SPREADSHEET_ID 미설정";
      badge.className = "badge badge-error";
    }
  } catch {
    const badge = document.getElementById("status-badge");
    badge.textContent = "서버 연결 실패";
    badge.className = "badge badge-error";
  }
}

async function loadPatients() {
  const select = document.getElementById("patient-select");
  select.innerHTML = '<option value="">로딩 중...</option>';
  try {
    const res = await fetch(`${API}/api/patients`);
    const data = await res.json();
    select.innerHTML = '<option value="">-- 환자를 선택하세요 --</option>';
    data.patients.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p["이름"];
      opt.textContent = `${p["이름"]} · ${p["수술부위"] || "수술부위 미입력"} · ${p["수술날"] || ""}`;
      select.appendChild(opt);
    });
  } catch (e) {
    select.innerHTML = '<option value="">환자 목록 로드 실패</option>';
    console.error(e);
  }
}

document.getElementById("patient-select").addEventListener("change", async function () {
  const name = this.value;
  const infoBox = document.getElementById("patient-info");
  if (!name) {
    infoBox.classList.add("hidden");
    return;
  }
  try {
    const res = await fetch(`${API}/api/patients/${encodeURIComponent(name)}`);
    const p = await res.json();
    renderPatientInfo(p);
    infoBox.classList.remove("hidden");
  } catch {
    infoBox.classList.add("hidden");
  }
});

function renderPatientInfo(p) {
  const grid = document.getElementById("patient-details");
  const fields = [
    ["수술 부위", p["수술부위"]],
    ["수술 날짜", p["수술날"]],
    ["수술 금액", p["수술금액"]],
    ["담당 원장", p["담당원장"] ? p["담당원장"] + " 원장님" : ""],
    ["말투 스타일", [p["연령대말투"], p["말투스타일"]].filter(Boolean).join(", ")],
    ["선호 키워드", p["선호키워드"]],
    ["활동 카페", p["활동카페"]],
    ["여우야 닉네임", p["여우야닉네임"]],
    ["성예사 닉네임", p["성예사닉네임"]],
    ["바비 닉네임", p["바비닉네임"]],
    ["강남언니 닉네임", p["강남언니닉네임"]],
    ["게시 이력 병원", p["게시이력병원"]],
  ];

  grid.innerHTML = fields
    .filter(([, v]) => v)
    .map(([k, v]) => `<div class="detail-item"><span class="detail-label">${k}</span><span class="detail-value">${v}</span></div>`)
    .join("");

  if (p["언급금지사항"]) {
    grid.innerHTML += `<div class="detail-item" style="grid-column:1/-1"><span class="detail-label">언급 금지</span><span class="detail-value warn">🚫 ${p["언급금지사항"]}</span></div>`;
  }
}

function selectPlatform(btn) {
  document.querySelectorAll("#platform-buttons .toggle-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  selectedPlatform = btn.dataset.value;
}

function selectPostType(btn) {
  document.querySelectorAll("#type-buttons .toggle-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  selectedPostType = btn.dataset.value;
}

async function generate() {
  const patientName = document.getElementById("patient-select").value;
  if (!patientName) return alert("환자를 선택해주세요.");
  if (!selectedPlatform) return alert("플랫폼을 선택해주세요.");
  if (!selectedPostType) return alert("글 종류를 선택해주세요.");

  const btn = document.getElementById("generate-btn");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>생성 중...';

  const resultCard = document.getElementById("result-card");
  resultCard.style.display = "none";

  try {
    const res = await fetch(`${API}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        patient_name: patientName,
        platform: selectedPlatform,
        post_type: selectedPostType,
        extra_context: document.getElementById("extra-context").value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "오류 발생");

    document.getElementById("result-meta").textContent =
      `${patientName} · ${selectedPlatform} ${selectedPostType} · ${data.result.length}자`;
    document.getElementById("result-text").value = data.result;
    resultCard.style.display = "flex";
    resultCard.scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    alert(`오류: ${e.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = "글 생성하기";
  }
}

function copyText() {
  const text = document.getElementById("result-text").value;
  navigator.clipboard.writeText(text).then(() => {
    const toast = document.getElementById("copy-toast");
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2000);
  });
}

loadConfig();
loadPatients();

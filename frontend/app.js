const API = "";

let selectedPlatform = "";
let selectedPostType = "";
let selectedPatientName = "";
let allPatients = [];
let activeHospital = "";

// ── 초기 로드 ──────────────────────────────────────────────
async function loadConfig() {
  try {
    const res = await fetch(`${API}/api/config`);
    const cfg = await res.json();
    const badge = document.getElementById("status-badge");
    if (cfg.sheets_configured) {
      badge.textContent = `AI: ${cfg.ai_provider === "claude" ? "Claude" : "GPT-4o"} · Sheets 연결됨`;
      badge.className = "badge badge-ok";
    } else {
      badge.textContent = "⚠ SPREADSHEET_ID 미설정 (샘플 데이터)";
      badge.className = "badge badge-warn";
    }
  } catch {
    const badge = document.getElementById("status-badge");
    badge.textContent = "서버 연결 실패";
    badge.className = "badge badge-error";
  }
}

async function loadPatients() {
  renderPatientList([]);
  document.getElementById("patient-list").innerHTML = '<div class="patient-list-empty">로딩 중...</div>';
  try {
    const [pRes, hRes] = await Promise.all([
      fetch(`${API}/api/patients`),
      fetch(`${API}/api/hospitals`),
    ]);
    const pData = await pRes.json();
    const hData = await hRes.json();
    allPatients = pData.patients;
    renderHospitalFilters(hData.hospitals);
    filterPatients();
  } catch (e) {
    document.getElementById("patient-list").innerHTML =
      '<div class="patient-list-empty">환자 목록을 불러오지 못했습니다.</div>';
    console.error(e);
  }
}

// ── 병원 필터 ──────────────────────────────────────────────
function renderHospitalFilters(hospitals) {
  const wrap = document.getElementById("hospital-filters");
  wrap.innerHTML = `<button class="toggle-btn active" data-hospital="" onclick="selectHospital(this)">전체</button>`;
  hospitals.forEach((h) => {
    const btn = document.createElement("button");
    btn.className = "toggle-btn";
    btn.dataset.hospital = h;
    btn.textContent = h;
    btn.onclick = function () { selectHospital(this); };
    wrap.appendChild(btn);
  });
}

function selectHospital(btn) {
  document.querySelectorAll("#hospital-filters .toggle-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  activeHospital = btn.dataset.hospital;
  filterPatients();
}

// ── 검색 & 필터링 ──────────────────────────────────────────
function filterPatients() {
  const query = document.getElementById("patient-search").value.trim().toLowerCase();
  const clearBtn = document.getElementById("search-clear");
  clearBtn.classList.toggle("hidden", query === "");

  const filtered = allPatients.filter((p) => {
    const matchHospital = !activeHospital || p["병원명"] === activeHospital;
    const matchName = !query || p["이름"].toLowerCase().includes(query);
    return matchHospital && matchName;
  });
  renderPatientList(filtered);
}

function clearSearch() {
  document.getElementById("patient-search").value = "";
  document.getElementById("search-clear").classList.add("hidden");
  filterPatients();
}

// ── 환자 목록 렌더링 ───────────────────────────────────────
function renderPatientList(patients) {
  const list = document.getElementById("patient-list");
  if (patients.length === 0) {
    list.innerHTML = '<div class="patient-list-empty">검색 결과가 없습니다.</div>';
    return;
  }
  list.innerHTML = patients.map((p) => `
    <div class="patient-item ${p["이름"] === selectedPatientName ? "selected" : ""}"
         onclick="selectPatient('${p["이름"]}')">
      <div class="patient-item-left">
        <span class="patient-item-name">${p["이름"]}</span>
        <span class="patient-item-sub">${p["수술부위"] || "수술부위 미입력"} · ${p["수술날"] || "-"}</span>
      </div>
      ${p["병원명"] ? `<span class="patient-item-hospital">${p["병원명"]}</span>` : ""}
    </div>
  `).join("");
}

// ── 환자 선택 ──────────────────────────────────────────────
async function selectPatient(name) {
  selectedPatientName = name;

  // 목록에서 선택 표시 업데이트
  document.querySelectorAll(".patient-item").forEach((el) => {
    el.classList.toggle("selected", el.querySelector(".patient-item-name")?.textContent === name);
  });

  try {
    const res = await fetch(`${API}/api/patients/${encodeURIComponent(name)}`);
    const p = await res.json();
    renderPatientInfo(p);
    document.getElementById("patient-info").classList.remove("hidden");
  } catch {
    document.getElementById("patient-info").classList.add("hidden");
  }
}

function clearPatient() {
  selectedPatientName = "";
  document.querySelectorAll(".patient-item").forEach((el) => el.classList.remove("selected"));
  document.getElementById("patient-info").classList.add("hidden");
}

function renderPatientInfo(p) {
  const grid = document.getElementById("patient-details");
  const fields = [
    ["병원", p["병원명"]],
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
    .map(([k, v]) => `
      <div class="detail-item">
        <span class="detail-label">${k}</span>
        <span class="detail-value">${v}</span>
      </div>`)
    .join("");

  if (p["언급금지사항"]) {
    grid.innerHTML += `
      <div class="detail-item" style="grid-column:1/-1">
        <span class="detail-label">언급 금지</span>
        <span class="detail-value warn">🚫 ${p["언급금지사항"]}</span>
      </div>`;
  }
}

// ── 플랫폼 / 글 종류 선택 ─────────────────────────────────
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

// ── 글 생성 ────────────────────────────────────────────────
async function generate() {
  if (!selectedPatientName) return alert("환자를 선택해주세요.");
  if (!selectedPlatform) return alert("플랫폼을 선택해주세요.");
  if (!selectedPostType) return alert("글 종류를 선택해주세요.");

  const btn = document.getElementById("generate-btn");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>생성 중...';
  document.getElementById("result-card").style.display = "none";

  try {
    const res = await fetch(`${API}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        patient_name: selectedPatientName,
        platform: selectedPlatform,
        post_type: selectedPostType,
        extra_context: document.getElementById("extra-context").value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "오류 발생");

    const textarea = document.getElementById("result-text");
    textarea.value = data.result;
    updateCharCount();
    document.getElementById("result-meta").textContent =
      `${selectedPatientName} · ${selectedPlatform} ${selectedPostType}`;
    document.getElementById("result-card").style.display = "flex";
    document.getElementById("result-card").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    alert(`오류: ${e.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = "글 생성하기";
  }
}

// ── 복사 / 글자수 ──────────────────────────────────────────
function copyText() {
  const text = document.getElementById("result-text").value;
  navigator.clipboard.writeText(text).then(() => {
    const toast = document.getElementById("copy-toast");
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2000);
  });
}

function updateCharCount() {
  const len = document.getElementById("result-text").value.length;
  document.getElementById("char-count").textContent = `${len}자`;
}

document.getElementById("result-text").addEventListener("input", updateCharCount);

// ── 시작 ───────────────────────────────────────────────────
loadConfig();
loadPatients();

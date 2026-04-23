const API = "";

let selectedPlatform = "";
let selectedPostType = "";
let selectedPatientName = "";
let selectedPriceOption = "yes";
let selectedHospitalFormat = "full";
let selectedPeriodOption = "yes";  // 기본값: 온점 사용
let allPatients = [];

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

async function loadPatients(forceRefresh = false) {
  renderPatientList([]);
  document.getElementById("patient-list").innerHTML = '<div class="patient-list-empty">로딩 중...</div>';
  const refreshBtn = document.getElementById("refresh-btn");
  if (refreshBtn) { refreshBtn.disabled = true; refreshBtn.textContent = "로딩 중..."; }
  try {
    if (forceRefresh) {
      await fetch(`${API}/api/patients/refresh`, { method: "POST" });
    }
    const res = await fetch(`${API}/api/patients`);
    const data = await res.json();
    allPatients = data.patients;
    filterPatients();
  } catch (e) {
    document.getElementById("patient-list").innerHTML =
      '<div class="patient-list-empty">환자 목록을 불러오지 못했습니다.</div>';
    console.error(e);
  } finally {
    if (refreshBtn) { refreshBtn.disabled = false; refreshBtn.textContent = "↺ 새로고침"; }
  }
}

// ── 검색 & 필터링 ──────────────────────────────────────────
function filterPatients() {
  const nameQuery = document.getElementById("patient-search").value.trim().toLowerCase();
  const hospitalQuery = document.getElementById("hospital-search").value.trim().toLowerCase();

  document.getElementById("search-clear").classList.toggle("hidden", nameQuery === "");
  document.getElementById("hospital-clear").classList.toggle("hidden", hospitalQuery === "");

  const filtered = allPatients.filter((p) => {
    const matchHospital = !hospitalQuery || (p["병원명"] || "").toLowerCase().includes(hospitalQuery);
    if (!matchHospital) return false;
    if (!nameQuery) return true;

    // 모든 필드에서 검색
    const searchableFields = [
      p["이름"], p["병원명"], p["수술부위"], p["수술날"],
      p["원장님"], p["말투"], p["게시글성향"], p["리스트"],
      p["특이사항"], p["비고"], p["년생"], p["추천인"],
      ...(p["카페목록"] || []),
    ];
    return searchableFields.some(v => v && String(v).toLowerCase().includes(nameQuery));
  });

  renderPatientList(filtered);
}

function clearSearch() {
  document.getElementById("patient-search").value = "";
  filterPatients();
}

function clearHospitalSearch() {
  document.getElementById("hospital-search").value = "";
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
    <div class="patient-item ${p["이름"] === selectedPatientName ? "selected" : ""} ${p["사용불가"] ? "disabled-account" : ""}"
         onclick="${p["사용불가"] ? "" : `selectPatient('${p["이름"]}')`}">
      <div class="patient-item-left">
        <span class="patient-item-name">${p["이름"]}${p["사용불가"] ? ' <span class="tag-disabled">사용 불가</span>' : ""}</span>
        <span class="patient-item-sub">${p["수술부위"] || "수술부위 미입력"} · ${p["수술날"] || "-"}</span>
      </div>
      ${p["병원명"] ? `<span class="patient-item-hospital">${p["병원명"]}</span>` : ""}
    </div>
  `).join("");
}

// ── 환자 선택 ──────────────────────────────────────────────
async function selectPatient(name) {
  selectedPatientName = name;

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
    ["병원",      p["병원명"]],
    ["수술",      [p["수술날"], p["수술부위"]].filter(Boolean).join(" · ")],
    ["담당 원장", p["원장님"] ? p["원장님"] + " 원장님" : ""],
    ["말투/성향", p["말투"]],
    ["게시글 방향", p["게시글성향"]],
    ["언급 병원",  p["리스트"]],
    ["년생",      p["년생"] ? p["년생"] + "년생" : ""],
  ];

  grid.innerHTML = fields
    .filter(([, v]) => v)
    .map(([k, v]) => `
      <div class="detail-item">
        <span class="detail-label">${k}</span>
        <span class="detail-value">${v}</span>
      </div>`)
    .join("");

  if (p["카페목록"]?.length) {
    const cafeHtml = p["카페목록"].map(c => `
      <div class="cafe-row">
        <span class="cafe-name">${c["카페"]}</span>
        <span class="cafe-nick">${c["닉네임"] || "-"}</span>
        ${c["마지막게시글"] ? `<span class="cafe-last">${c["마지막게시글"]}</span>` : ""}
      </div>`).join("");
    grid.innerHTML += `
      <div class="detail-item cafe-block" style="grid-column:1/-1">
        <span class="detail-label">카페 / 닉네임</span>
        <div class="cafe-list">${cafeHtml}</div>
      </div>`;
  }

  if (p["특이사항"]) {
    grid.innerHTML += `
      <div class="detail-item" style="grid-column:1/-1">
        <span class="detail-label">주의사항</span>
        <span class="detail-value warn">🚫 ${p["특이사항"]}</span>
      </div>`;
  }

  const platformWrap = document.getElementById("platform-buttons");
  const hint = document.getElementById("platform-hint");
  selectedPlatform = "";

  if (p["카페목록"]?.length) {
    hint.textContent = "";
    platformWrap.innerHTML = p["카페목록"]
      .filter(c => c["카페"])
      .map(c => `
        <button class="toggle-btn" data-value="${c['카페']}" onclick="selectPlatform(this)">
          ${c["카페"]}<span class="platform-nick">${c["닉네임"] ? " · " + c["닉네임"] : ""}</span>
        </button>`)
      .join("");
  } else {
    hint.textContent = "카페 정보 없음";
    platformWrap.innerHTML = '<span class="platform-empty-msg">카페 정보가 없습니다</span>';
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

function selectPrice(btn) {
  document.querySelectorAll("#price-yes, #price-no").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  selectedPriceOption = btn.dataset.value;
}

function selectHospitalFormat(btn) {
  document.querySelectorAll("#hospital-full, #hospital-abbr").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  selectedHospitalFormat = btn.dataset.value;
}

function selectPeriod(btn) {
  document.querySelectorAll("#period-yes, #period-no").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  selectedPeriodOption = btn.dataset.value;
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
        char_limit: parseInt(document.getElementById("char-limit").value) || 0,
        include_price: selectedPriceOption === "yes",
        hospital_format: selectedHospitalFormat,
        use_period: selectedPeriodOption === "yes",
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
    renderReview(data.review);
    document.getElementById("result-card").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    alert(`오류: ${e.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = "글 생성하기";
  }
}

// ── 검수 결과 렌더링 ───────────────────────────────────────
function renderReview(review) {
  const panel = document.getElementById("review-panel");
  if (!review || review.error) { panel.classList.add("hidden"); return; }

  const ICON = { pass: "✓", warn: "△", fail: "✗" };
  const badge = document.getElementById("review-badge");
  const labelMap = { pass: "통과", warn: "주의", fail: "수정 필요" };
  badge.textContent = labelMap[review.종합] || "";
  badge.className = `review-badge review-badge-${review.종합}`;

  document.getElementById("review-items").innerHTML = (review.항목 || []).map(item => `
    <div class="review-item review-item-${item.결과}">
      <span class="review-icon">${ICON[item.결과] || "?"}</span>
      <span class="review-item-name">${item.이름}</span>
      <span class="review-item-comment">${item.코멘트}</span>
    </div>
  `).join("");

  document.getElementById("review-summary").textContent = review.총평 || "";
  panel.classList.remove("hidden");
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

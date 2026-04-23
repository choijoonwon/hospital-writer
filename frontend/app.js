const API = "";

let selectedPlatform = "";
let selectedPostType = "";
let selectedPatientName = "";
let selectedHospitalFormat = "full";
let selectedPeriodOption = "yes";
let allPatients = [];

// 대량 모드 상태
let currentMode = "individual";
let bulkSelectedPatients = [];
let bulkPostType = "";
let bulkHospitalFormat = "full";
let bulkPeriodOption = "yes";

// ── 모드 전환 ──────────────────────────────────────────────
function switchMode(mode) {
  currentMode = mode;
  document.getElementById("section-individual").classList.toggle("hidden", mode !== "individual");
  document.getElementById("section-bulk").classList.toggle("hidden", mode !== "bulk");
  document.getElementById("tab-individual").classList.toggle("active", mode === "individual");
  document.getElementById("tab-bulk").classList.toggle("active", mode === "bulk");
  if (mode === "bulk") filterBulkPatients();
}

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
  document.getElementById("patient-list").innerHTML = '<div class="patient-list-empty">로딩 중...</div>';
  document.getElementById("bulk-patient-list").innerHTML = '<div class="patient-list-empty">로딩 중...</div>';
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
    filterBulkPatients();
  } catch (e) {
    document.getElementById("patient-list").innerHTML = '<div class="patient-list-empty">환자 목록을 불러오지 못했습니다.</div>';
    document.getElementById("bulk-patient-list").innerHTML = '<div class="patient-list-empty">환자 목록을 불러오지 못했습니다.</div>';
    console.error(e);
  } finally {
    if (refreshBtn) { refreshBtn.disabled = false; refreshBtn.textContent = "↺ 새로고침"; }
  }
}

// ── 개별 모드: 검색 & 필터 ────────────────────────────────
function _filterBase(patients, nameQuery, hospitalQuery) {
  return patients.filter((p) => {
    const matchHospital = !hospitalQuery || (p["병원명"] || "").toLowerCase().includes(hospitalQuery);
    if (!matchHospital) return false;
    if (!nameQuery) return true;
    const searchableFields = [
      p["이름"], p["병원명"], p["수술부위"], p["수술날"],
      p["원장님"], p["말투"], p["게시글성향"], p["리스트"],
      p["특이사항"], p["비고"], p["년생"], p["추천인"],
      ...(p["카페목록"] || []),
    ];
    return searchableFields.some(v => v && String(v).toLowerCase().includes(nameQuery));
  });
}

function filterPatients() {
  const nameQuery = document.getElementById("patient-search").value.trim().toLowerCase();
  const hospitalQuery = document.getElementById("hospital-search").value.trim().toLowerCase();
  document.getElementById("search-clear").classList.toggle("hidden", nameQuery === "");
  document.getElementById("hospital-clear").classList.toggle("hidden", hospitalQuery === "");
  renderPatientList(_filterBase(allPatients, nameQuery, hospitalQuery));
}

function clearSearch() { document.getElementById("patient-search").value = ""; filterPatients(); }
function clearHospitalSearch() { document.getElementById("hospital-search").value = ""; filterPatients(); }

// ── 개별 모드: 환자 목록 렌더링 ───────────────────────────
function renderPatientList(patients) {
  const list = document.getElementById("patient-list");
  if (patients.length === 0) {
    list.innerHTML = '<div class="patient-list-empty">검색 결과가 없습니다.</div>';
    return;
  }
  list.innerHTML = patients.map((p) => `
    <div class="patient-item ${p["이름"] === selectedPatientName ? "selected" : ""} ${p["사용불가"] ? "disabled-account" : ""}"
         onclick="${p["사용불가"] ? "" : `selectPatient('${p["이름"].replace(/'/g, "\\'")}')`}">
      <div class="patient-item-left">
        <span class="patient-item-name">${p["이름"]}${p["사용불가"] ? ' <span class="tag-disabled">사용 불가</span>' : ""}</span>
        <span class="patient-item-sub">${p["수술부위"] || "수술부위 미입력"} · ${p["수술날"] || "-"}</span>
      </div>
      ${p["병원명"] ? `<span class="patient-item-hospital">${p["병원명"]}</span>` : ""}
    </div>
  `).join("");
}

// ── 개별 모드: 환자 선택 ──────────────────────────────────
async function selectPatient(name) {
  selectedPatientName = name;
  document.querySelectorAll("#patient-list .patient-item").forEach((el) => {
    el.classList.toggle("selected", el.querySelector(".patient-item-name")?.textContent.trim() === name);
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
  document.querySelectorAll("#patient-list .patient-item").forEach((el) => el.classList.remove("selected"));
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
  grid.innerHTML = fields.filter(([, v]) => v).map(([k, v]) => `
    <div class="detail-item">
      <span class="detail-label">${k}</span>
      <span class="detail-value">${v}</span>
    </div>`).join("");

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
    platformWrap.innerHTML = p["카페목록"].filter(c => c["카페"]).map(c => `
      <button class="toggle-btn" data-value="${c['카페']}" onclick="selectPlatform(this)">
        ${c["카페"]}<span class="platform-nick">${c["닉네임"] ? " · " + c["닉네임"] : ""}</span>
      </button>`).join("");
  } else {
    hint.textContent = "카페 정보 없음";
    platformWrap.innerHTML = '<span class="platform-empty-msg">카페 정보가 없습니다</span>';
  }
}

// ── 개별 모드: 설정 선택 ──────────────────────────────────
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

// ── 개별 모드: 글 생성 ────────────────────────────────────
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
  const labelMap = { pass: "통과", warn: "주의", fail: "수정 필요" };
  const badge = document.getElementById("review-badge");
  badge.textContent = labelMap[review.종합] || "";
  badge.className = `review-badge review-badge-${review.종합}`;
  document.getElementById("review-items").innerHTML = (review.항목 || []).map(item => `
    <div class="review-item review-item-${item.결과}">
      <span class="review-icon">${ICON[item.결과] || "?"}</span>
      <span class="review-item-name">${item.이름}</span>
      <span class="review-item-comment">${item.코멘트}</span>
    </div>`).join("");
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


// ════════════════════════════════════════════════════════════
// 대량 모드
// ════════════════════════════════════════════════════════════

// ── 대량 모드: 검색 & 필터 ───────────────────────────────
function filterBulkPatients() {
  const nameQuery = document.getElementById("bulk-patient-search").value.trim().toLowerCase();
  const hospitalQuery = document.getElementById("bulk-hospital-search").value.trim().toLowerCase();
  document.getElementById("bulk-search-clear").classList.toggle("hidden", nameQuery === "");
  document.getElementById("bulk-hospital-clear").classList.toggle("hidden", hospitalQuery === "");
  renderBulkPatientList(_filterBase(allPatients, nameQuery, hospitalQuery));
}

function clearBulkSearch() { document.getElementById("bulk-patient-search").value = ""; filterBulkPatients(); }
function clearBulkHospitalSearch() { document.getElementById("bulk-hospital-search").value = ""; filterBulkPatients(); }

// ── 대량 모드: 환자 목록 렌더링 (체크박스) ───────────────
function renderBulkPatientList(patients) {
  const list = document.getElementById("bulk-patient-list");
  if (patients.length === 0) {
    list.innerHTML = '<div class="patient-list-empty">검색 결과가 없습니다.</div>';
    return;
  }
  list.innerHTML = patients.map((p) => {
    const isChecked = bulkSelectedPatients.some(s => s["이름"] === p["이름"]);
    const isDisabled = p["사용불가"];
    return `
      <div class="patient-item ${isDisabled ? "disabled-account" : ""}" style="cursor:${isDisabled ? "not-allowed" : "pointer"}"
           onclick="${isDisabled ? "" : `toggleBulkPatient('${p["이름"].replace(/'/g, "\\'")}')`}">
        <div class="patient-item-left">
          <span class="patient-item-name">${p["이름"]}${isDisabled ? ' <span class="tag-disabled">사용 불가</span>' : ""}</span>
          <span class="patient-item-sub">${p["수술부위"] || "수술부위 미입력"} · ${p["수술날"] || "-"}</span>
        </div>
        ${p["병원명"] ? `<span class="patient-item-hospital">${p["병원명"]}</span>` : ""}
        ${!isDisabled ? `<input type="checkbox" class="patient-item-checkbox" ${isChecked ? "checked" : ""}
          onclick="event.stopPropagation(); toggleBulkPatient('${p["이름"].replace(/'/g, "\\'")}')" />` : ""}
      </div>`;
  }).join("");
}

// ── 대량 모드: 계정 선택 토글 ────────────────────────────
function toggleBulkPatient(name) {
  const patient = allPatients.find(p => p["이름"] === name);
  if (!patient || patient["사용불가"]) return;
  const idx = bulkSelectedPatients.findIndex(p => p["이름"] === name);
  if (idx === -1) {
    bulkSelectedPatients.push(patient);
  } else {
    bulkSelectedPatients.splice(idx, 1);
  }
  filterBulkPatients();
  renderBulkSelectedPanel();
}

function bulkSelectAll() {
  const nameQuery = document.getElementById("bulk-patient-search").value.trim().toLowerCase();
  const hospitalQuery = document.getElementById("bulk-hospital-search").value.trim().toLowerCase();
  const visible = _filterBase(allPatients, nameQuery, hospitalQuery).filter(p => !p["사용불가"]);
  visible.forEach(p => {
    if (!bulkSelectedPatients.some(s => s["이름"] === p["이름"])) {
      bulkSelectedPatients.push(p);
    }
  });
  filterBulkPatients();
  renderBulkSelectedPanel();
}

function bulkClearAll() {
  bulkSelectedPatients = [];
  filterBulkPatients();
  renderBulkSelectedPanel();
}

function removeBulkPatient(name) {
  bulkSelectedPatients = bulkSelectedPatients.filter(p => p["이름"] !== name);
  filterBulkPatients();
  renderBulkSelectedPanel();
}

function renderBulkSelectedPanel() {
  const panel = document.getElementById("bulk-selected-panel");
  const count = bulkSelectedPatients.length;
  document.getElementById("bulk-selected-count").textContent = `${count}명`;

  if (count === 0) {
    panel.classList.add("hidden");
    return;
  }
  panel.classList.remove("hidden");

  document.getElementById("bulk-selected-list").innerHTML = bulkSelectedPatients.map(p => `
    <div class="bulk-chip">
      <span>${p["이름"]}</span>
      <span style="font-size:11px;color:#9990e8;font-weight:400">${p["병원명"] || ""}</span>
      <button class="bulk-chip-remove" onclick="removeBulkPatient('${p["이름"].replace(/'/g, "\\'")}')">✕</button>
    </div>`).join("");
}

// ── 대량 모드: 설정 선택 ──────────────────────────────────
function selectBulkPostType(btn) {
  document.querySelectorAll("#bulk-type-buttons .toggle-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  bulkPostType = btn.dataset.value;
}
function selectBulkHospitalFormat(btn) {
  document.querySelectorAll("#bulk-hospital-full, #bulk-hospital-abbr").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  bulkHospitalFormat = btn.dataset.value;
}
function selectBulkPeriod(btn) {
  document.querySelectorAll("#bulk-period-yes, #bulk-period-no").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  bulkPeriodOption = btn.dataset.value;
}

// ── 대량 모드: 생성 ───────────────────────────────────────
async function generateBulk() {
  if (bulkSelectedPatients.length === 0) return alert("계정을 선택해주세요.");
  if (!bulkPostType) return alert("글 종류를 선택해주세요.");

  const btn = document.getElementById("bulk-generate-btn");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>생성 중...';

  const resultCard = document.getElementById("bulk-result-card");
  const resultsList = document.getElementById("bulk-results-list");
  const progressText = document.getElementById("bulk-progress-text");
  const progressBarWrap = document.getElementById("bulk-progress-bar-wrap");
  const progressBar = document.getElementById("bulk-progress-bar");

  resultCard.classList.remove("hidden");
  resultsList.innerHTML = "";
  progressBarWrap.classList.remove("hidden");
  resultCard.scrollIntoView({ behavior: "smooth" });

  const total = bulkSelectedPatients.length;
  const extraContext = document.getElementById("bulk-extra-context").value;
  const charLimit = parseInt(document.getElementById("bulk-char-limit").value) || 0;

  // 미리 로딩 카드 생성
  bulkSelectedPatients.forEach((p, i) => {
    const div = document.createElement("div");
    div.className = "bulk-result-item generating";
    div.id = `bulk-item-${i}`;
    div.innerHTML = `
      <div class="bulk-result-header">
        <span class="bulk-result-name">${p["이름"]}</span>
        <span class="bulk-result-platform">${p["병원명"] || ""}</span>
        <span class="bulk-result-toggle" style="color:#bbb">대기 중</span>
      </div>`;
    resultsList.appendChild(div);
  });

  for (let i = 0; i < total; i++) {
    const p = bulkSelectedPatients[i];
    const platform = p["카페목록"]?.[0]?.["카페"] || "";
    const itemEl = document.getElementById(`bulk-item-${i}`);

    progressText.textContent = `${i + 1} / ${total} 생성 중...`;
    progressBar.style.width = `${((i) / total) * 100}%`;

    // 로딩 표시
    itemEl.innerHTML = `
      <div class="bulk-result-header">
        <span class="bulk-result-name">${p["이름"]}</span>
        <span class="bulk-result-platform">${platform || "카페 없음"}</span>
        <span class="bulk-result-toggle" style="color:#aaa">생성 중...</span>
      </div>
      <div class="bulk-spinner-wrap"><span class="spinner" style="border-color:rgba(108,99,255,0.3);border-top-color:#6c63ff"></span>AI가 글을 작성하고 있어요</div>`;

    try {
      const res = await fetch(`${API}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_name: p["이름"],
          platform: platform,
          post_type: bulkPostType,
          extra_context: extraContext,
          char_limit: charLimit,
          hospital_format: bulkHospitalFormat,
          use_period: bulkPeriodOption === "yes",
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "오류");
      renderBulkResultItem(itemEl, p, platform, data);
    } catch (e) {
      itemEl.innerHTML = `
        <div class="bulk-result-header">
          <span class="bulk-result-name">${p["이름"]}</span>
          <span class="bulk-result-platform">${platform || "카페 없음"}</span>
          <span class="bulk-result-toggle" style="color:#c62828">오류: ${e.message}</span>
        </div>`;
    }
  }

  progressText.textContent = `총 ${total}개 완료`;
  progressBar.style.width = "100%";
  setTimeout(() => progressBarWrap.classList.add("hidden"), 1500);

  btn.disabled = false;
  btn.innerHTML = "대량 생성하기";
}

function renderBulkResultItem(el, patient, platform, data) {
  const ICON = { pass: "✓", warn: "△", fail: "✗" };
  const review = data.review;
  const reviewBadgeHtml = (review && !review.error)
    ? `<span class="review-badge review-badge-${review.종합}" style="font-size:10px;padding:2px 8px">${{pass:"통과",warn:"주의",fail:"수정 필요"}[review.종합]||""}</span>`
    : "";

  const uid = `bulk-ta-${Math.random().toString(36).slice(2)}`;
  const isOpen = true;

  el.className = "bulk-result-item";
  el.innerHTML = `
    <div class="bulk-result-header" onclick="toggleBulkItem(this)">
      <span class="bulk-result-name">${patient["이름"]}</span>
      <span class="bulk-result-platform">${platform || "카페 없음"}</span>
      ${reviewBadgeHtml}
      <span class="bulk-result-toggle">▲</span>
    </div>
    <div class="bulk-result-body">
      <textarea id="${uid}" class="result-textarea" style="min-height:160px">${data.result}</textarea>
      <div class="bulk-result-actions">
        <span style="font-size:12px;color:#aaa;flex:1">${data.result.length}자</span>
        <button class="btn btn-copy btn" style="padding:8px 16px;font-size:13px" onclick="copyBulkText('${uid}')">복사</button>
      </div>
      ${review && !review.error ? `
      <div style="display:flex;flex-direction:column;gap:5px;margin-top:4px">
        ${(review.항목 || []).map(item => `
          <div class="review-item review-item-${item.결과}" style="padding:5px 8px">
            <span class="review-icon">${ICON[item.결과]||"?"}</span>
            <span class="review-item-name">${item.이름}</span>
            <span class="review-item-comment">${item.코멘트}</span>
          </div>`).join("")}
        <div class="review-summary">${review.총평 || ""}</div>
      </div>` : ""}
    </div>`;
}

function toggleBulkItem(header) {
  const body = header.nextElementSibling;
  const toggle = header.querySelector(".bulk-result-toggle");
  if (body.style.display === "none") {
    body.style.display = "";
    toggle.textContent = "▲";
  } else {
    body.style.display = "none";
    toggle.textContent = "▼";
  }
}

function copyBulkText(uid) {
  const text = document.getElementById(uid).value;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector(`#${uid} ~ .bulk-result-actions .btn-copy`);
  });
}

// ── 시작 ───────────────────────────────────────────────────
loadConfig();
loadPatients();

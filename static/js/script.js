/* ── GLOBAL UTILITIES ───────────────────────────────────── */

// Mark active sidebar link
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  document.querySelectorAll(".sidebar nav a").forEach(a => {
    if (a.getAttribute("href") === path) a.classList.add("active");
  });
});

// Toast helper
function showToast(msg = "Done!", color = "#22d3a0") {
  let t = document.getElementById("toast");
  if (!t) {
    t = document.createElement("div");
    t.id = "toast";
    document.body.appendChild(t);
  }
  t.style.background = color;
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 3000);
}

// Grade from score
function gradeFromScore(score) {
  if (score >= 85) return "A";
  if (score >= 70) return "B";
  if (score >= 55) return "C";
  if (score >= 40) return "D";
  return "F";
}

// Progress bar builder
function buildProgress(pct, amber = false) {
  return `
    <div class="progress-wrap">
      <div class="progress-bar">
        <div class="progress-fill${amber ? " amber" : ""}" style="width:${pct}%"></div>
      </div>
      <span class="progress-val">${pct}%</span>
    </div>`;
}

/* ── PREDICT PAGE ───────────────────────────────────────── */
async function runPrediction() {
  const get = id => parseFloat(document.getElementById(id)?.value) || 0;

  const payload = {
    age:             get("age"),
    gender:          get("gender"),
    gpa:             get("gpa"),
    studyTime:       get("studyTime"),
    absences:        get("absences"),
    tutoring:        get("tutoring"),
    parentalSupport: get("parentalSupport"),
    extracurricular: get("extracurricular"),
    sports:          get("sports"),
    music:           get("music"),
    volunteering:    get("volunteering"),
  };

  try {
    const res  = await fetch("/api/predict", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });
    const data = await res.json();
    renderPredictResults(data, payload);
    showToast("✓ Report generated");
  } catch (err) {
    showToast("⚠ Server error — check Flask is running", "#f87171");
  }
}

function renderPredictResults(data, input) {
  const wrap = document.getElementById("results");
  if (!wrap) return;
  wrap.style.display = "block";

  // KPIs
  setText("predGpa",         data.predicted_gpa);
  setText("currentGpa",      input.gpa);
  setText("predGrade",       data.predicted_grade);
  setText("predAttendance",  data.predicted_attendance + "%");

  // Subject table
  const tbody = document.getElementById("subjectTableBody");
  if (tbody) {
    tbody.innerHTML = data.subjects.map(s => {
      const g = gradeFromScore(s.score);
      return `
        <tr>
          <td style="font-weight:600">${s.name}</td>
          <td>${buildProgress(s.score, s.score < 50)}</td>
          <td>${buildProgress(s.attendance, s.attendance < 70)}</td>
          <td><div class="grade grade-${g}">${g}</div></td>
        </tr>`;
    }).join("");
  }

  // Recommendations
  const recList = document.getElementById("recList");
  if (recList) {
    const icons = ["📖","⏰","🏫","📝","⚠️","🔔"];
    recList.innerHTML = data.recommendations.map((r, i) => `
      <div class="rec-item">
        <div class="rec-icon">${icons[i] || "💡"}</div>
        <div class="rec-text">${r}</div>
      </div>`).join("");
  }

  wrap.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ── ANALYTICS PAGE ─────────────────────────────────────── */
async function loadAnalytics() {
  try {
    const res  = await fetch("/api/analytics");
    const data = await res.json();
    setText("totalStudents", data.total_students);
    setText("avgGpa",        data.avg_gpa);
    setText("avgAbsences",   data.avg_absences);
    setText("avgStudyTime",  data.avg_study_time + " hrs");
    setText("tutoringPct",   data.tutoring_pct + "%");
  } catch (_) {}
}

/* ── ATTENDANCE PAGE ────────────────────────────────────── */
async function lookupAttendance() {
  const sid = parseInt(document.getElementById("attendanceSid")?.value);
  if (!sid) return showToast("Enter a Student ID", "#f59e0b");
  try {
    const res  = await fetch(`/api/student/${sid}`);
    const data = await res.json();
    if (data.error) return showToast("Student not found", "#f87171");
    setText("attStudentId",  data.StudentID);
    setText("attGpa",        parseFloat(data.GPA).toFixed(2));
    setText("attAbsences",   data.Absences);
    setText("attStudyTime",  parseFloat(data.StudyTimeWeekly).toFixed(1));
    const pct = Math.max(0, Math.min(100, 100 - data.Absences * 1.5));
    setText("attPercent",    pct.toFixed(1) + "%");
    const bar = document.getElementById("attBar");
    if (bar) bar.style.width = pct + "%";
    document.getElementById("attendanceResult").style.display = "block";
  } catch (_) {
    showToast("Server error", "#f87171");
  }
}

/* ── DASHBOARD PAGE ─────────────────────────────────────── */
async function loadDashboard() {
  await loadAnalytics();
}

/* ── HELPER ─────────────────────────────────────────────── */
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// Auto-init
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("totalStudents")) loadAnalytics();
  if (document.getElementById("attBar"))        {} // attendance page ready
});

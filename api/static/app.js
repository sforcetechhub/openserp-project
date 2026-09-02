const AUTH_REQUIRED = Boolean(window.AUTH_REQUIRED);
const keyInput = document.getElementById("api-key");
const healthPill = document.getElementById("health-pill");

if (keyInput) {
  keyInput.value = sessionStorage.getItem("openserp_api_key") || "";
  keyInput.addEventListener("change", () => {
    sessionStorage.setItem("openserp_api_key", keyInput.value.trim());
  });
}

function headers() {
  const result = { Accept: "application/json" };
  const key = keyInput ? keyInput.value.trim() : "";
  if (AUTH_REQUIRED && key) {
    result.Authorization = `Bearer ${key}`;
  }
  return result;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { ...headers(), ...(options.headers || {}) },
  });
  const raw = await response.text();
  let data = {};
  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    data = { reason: raw.slice(0, 240) };
  }
  if (!response.ok) {
    let detail = data.detail;
    if (Array.isArray(detail)) {
      detail = detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
    } else if (detail && typeof detail === "object") {
      detail = detail.reason || detail.message || JSON.stringify(detail);
    }
    const message = data.reason || data.code || detail || `Request failed (${response.status})`;
    const error = new Error(message);
    error.status = response.status;
    error.payload = data;
    throw error;
  }
  return data;
}

function showStatus(node, message, isError = false) {
  node.hidden = !message;
  node.textContent = message || "";
  node.classList.toggle("error", Boolean(isError));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(".panel").forEach((panel) => {
      panel.hidden = panel.id !== `panel-${tab.dataset.tab}`;
    });
  });
});

async function refreshHealth() {
  try {
    const data = await fetch("/health").then((res) => res.json());
    const ready = Boolean(data.openserp_ready);
    healthPill.textContent = ready ? "openserp ready" : "openserp degraded";
    healthPill.className = `pill ${ready ? "ok" : "bad"}`;
  } catch {
    healthPill.textContent = "api unreachable";
    healthPill.className = "pill bad";
  }
}

refreshHealth();
setInterval(refreshHealth, 15000);

const searchForm = document.getElementById("search-form");
const searchStatus = document.getElementById("search-status");
const searchResults = document.getElementById("search-results");

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(searchForm);
  const params = new URLSearchParams();
  params.set("text", String(form.get("text") || "").trim());
  params.set("limit", String(form.get("limit") || "10"));
  const region = String(form.get("region") || "").trim();
  if (region) params.set("region", region);
  const extract = Number(form.get("extract") || 0);
  if (extract) params.set("extract", String(extract));

  const mega = form.get("mega") === "on";
  if (mega) {
    params.set("mode", String(form.get("mode") || "balanced"));
    params.set("engines", "duckduckgo,ecosia,bing");
  } else {
    params.set("engine", String(form.get("engine") || "duckduckgo"));
  }

  const button = searchForm.querySelector("button");
  button.disabled = true;
  showStatus(searchStatus, "Searching…");
  searchResults.innerHTML = "";
  try {
    const path = mega ? `/api/mega?${params}` : `/api/search?${params}`;
    const data = await api(path);
    const items = data.results || [];
    const took = data.meta?.took_ms;
    showStatus(
      searchStatus,
      `${items.length} results${took ? ` in ${took} ms` : ""}${data.meta?.engines_failed?.length ? ` · failed: ${data.meta.engines_failed.join(", ")}` : ""}`,
    );
    searchResults.innerHTML = items
      .map((item) => {
        const extracted = item.extracted?.content
          ? `<pre class="extracted">${escapeHtml(item.extracted.content.slice(0, 1200))}</pre>`
          : "";
        return `<article class="card">
          <div><span class="rank">#${escapeHtml(item.rank ?? "")}</span><strong>${escapeHtml(item.engine || "")}</strong></div>
          <h3><a href="${escapeHtml(item.url || "#")}" target="_blank" rel="noreferrer">${escapeHtml(item.title || item.url)}</a></h3>
          <div class="url">${escapeHtml(item.display_url || item.url || "")}</div>
          <p class="snippet">${escapeHtml(item.snippet || "")}</p>
          ${extracted}
        </article>`;
      })
      .join("");
  } catch (error) {
    showStatus(searchStatus, error.message, true);
  } finally {
    button.disabled = false;
  }
});

const imageForm = document.getElementById("image-form");
const imageStatus = document.getElementById("image-status");
const imageResults = document.getElementById("image-results");

imageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(imageForm);
  const params = new URLSearchParams();
  params.set("text", String(form.get("text") || "").trim());
  params.set("limit", String(form.get("limit") || "12"));
  if (form.get("mega") === "on") {
    params.set("engines", "bing,google");
  } else {
    params.set("engine", String(form.get("engine") || "bing"));
  }
  const button = imageForm.querySelector("button");
  button.disabled = true;
  showStatus(imageStatus, "Fetching images…");
  imageResults.innerHTML = "";
  try {
    const data = await api(`/api/images?${params}`);
    const items = data.results || [];
    showStatus(imageStatus, `${items.length} images`);
    imageResults.innerHTML = items
      .map((item) => {
        const src = item.image?.thumbnail || item.image?.url || "";
        const href = item.source?.page_url || item.image?.url || "#";
        return `<a class="image-card" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">
          <img src="${escapeHtml(src)}" alt="${escapeHtml(item.title || "image")}" />
          <p>${escapeHtml(item.title || item.source?.domain || "")}</p>
        </a>`;
      })
      .join("");
  } catch (error) {
    showStatus(imageStatus, error.message, true);
  } finally {
    button.disabled = false;
  }
});

const extractForm = document.getElementById("extract-form");
const extractStatus = document.getElementById("extract-status");
const extractResult = document.getElementById("extract-result");

extractForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(extractForm);
  const button = extractForm.querySelector("button");
  button.disabled = true;
  showStatus(extractStatus, "Extracting…");
  extractResult.innerHTML = "";
  try {
    const data = await api("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: String(form.get("url") || "").trim(),
        mode: form.get("mode") || "auto",
        clean: true,
      }),
    });
    showStatus(extractStatus, data.meta?.mode_used ? `mode: ${data.meta.mode_used}` : "done");
    extractResult.innerHTML = `<h2>${escapeHtml(data.title || data.url || "Extract")}</h2>
      <p class="url">${escapeHtml(data.url || "")}</p>
      <pre>${escapeHtml(data.markdown || data.text || "")}</pre>`;
  } catch (error) {
    showStatus(extractStatus, error.message, true);
  } finally {
    button.disabled = false;
  }
});

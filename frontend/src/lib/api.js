const API_BASE = import.meta.env.VITE_API_BASE || "";

function safeJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const text = await response.text();
  const data = text ? safeJson(text) : {};
  if (!response.ok) {
    throw new Error(data.detail || `请求失败：HTTP ${response.status}`);
  }
  return data;
}

export function getConfig() {
  return request("/api/config");
}

export function generatePack(payload) {
  return request("/api/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateImage(payload) {
  return request("/api/generate-image", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function editImage({ file, prompt, model, size = "1024x1024" }) {
  const form = new FormData();
  form.append("image", file);
  form.append("prompt", prompt);
  form.append("model", model);
  form.append("size", size);

  const response = await fetch(`${API_BASE}/api/edit-image`, {
    method: "POST",
    body: form,
  });
  const text = await response.text();
  const data = text ? safeJson(text) : {};
  if (!response.ok) {
    throw new Error(data.detail || `图片改图失败：HTTP ${response.status}`);
  }
  return data;
}

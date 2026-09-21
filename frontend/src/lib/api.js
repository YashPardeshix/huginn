const API_BASE = "http://localhost:8000";

export async function fetchRuns() {
  const res = await fetch(`${API_BASE}/runs`);
  if (!res.ok) throw new Error("Failed to fetch runs");
  return res.json();
}

export async function fetchRun(runId) {
  const res = await fetch(`${API_BASE}/runs/${runId}`);
  if (!res.ok) throw new Error("Failed to fetch run");
  return res.json();
}

export async function fetchRunStatus(runId) {
  const res = await fetch(`${API_BASE}/runs/${runId}/status`);
  if (!res.ok) throw new Error("Failed to fetch run status");
  return res.json();
}

export async function fetchMetricsTrend() {
  const res = await fetch(`${API_BASE}/metrics/trend`);
  if (!res.ok) throw new Error("Failed to fetch metrics trend");
  return res.json();
}

export async function fetchRepositories() {
  const res = await fetch(`${API_BASE}/repositories`);
  if (!res.ok) throw new Error("Failed to fetch repositories");
  return res.json();
}

export async function fetchAuditLog() {
  const res = await fetch(`${API_BASE}/audit`);
  if (!res.ok) throw new Error("Failed to fetch audit log");
  return res.json();
}

export async function submitIssueUrl(url) {
  const res = await fetch(`${API_BASE}/runs/from-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ github_issue_url: url }),
  });
  if (!res.ok) throw new Error("Failed to submit issue URL");
  return res.json();
}

export async function approveRun(runId) {
  const res = await fetch(`${API_BASE}/runs/${runId}/approve`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to approve run");
  return res.json();
}

export async function submitHumanFix(runId, humanFix) {
  const res = await fetch(`${API_BASE}/runs/${runId}/human-fix`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ human_fix: humanFix }),
  });
  if (!res.ok) throw new Error("Failed to submit human fix");
  return res.json();
}

export async function deleteRun(runId) {
  const res = await fetch(`${API_BASE}/runs/${runId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete run");
  return res.json();
}
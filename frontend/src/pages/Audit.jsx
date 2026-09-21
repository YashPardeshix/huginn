import { useState, useEffect } from "react";
import { fetchAuditLog } from "../lib/api";

function eventColor(entry) {
  if (entry.event_type === "pipeline_error") return "text-primary";
  if (entry.github_status && entry.github_status.startsWith("failed")) return "text-primary";
  if (entry.verdict === "trustworthy") return "text-trustworthy";
  return "text-on-surface-muted";
}

export default function Audit() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAuditLog()
      .then((data) => setEntries(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-12">
      <div className="font-mono text-xs tracking-widest text-primary mb-3">
        AUDIT
      </div>
      <h1 className="font-display font-bold text-4xl text-on-surface mb-6">
        Operational Audit Log
      </h1>

      {loading ? (
        <div className="font-mono text-sm text-on-surface-muted">
          Loading...
        </div>
      ) : error ? (
        <div className="font-mono text-sm text-primary">{error}</div>
      ) : entries.length === 0 ? (
        <div className="border border-outline p-8 text-center font-mono text-sm text-on-surface-muted">
          No audit events logged yet. Approve a run or trigger a pipeline
          error to see entries here.
        </div>
      ) : (
        <div className="border border-outline">
          {entries.map((e, i) => (
            <div
              key={i}
              className="flex justify-between items-center px-4 py-3 border-b border-outline last:border-b-0"
            >
              <div>
                <span className={`font-mono text-xs tracking-widest ${eventColor(e)}`}>
                  {e.event_type.toUpperCase()}
                </span>
                <span className="font-mono text-xs text-on-surface-dim ml-3">
                  {e.thread_id.slice(0, 8)}
                </span>
              </div>
              <div className="font-mono text-xs text-on-surface-muted">
                {e.event_type === "approval"
                  ? `${e.verdict} · ${e.similarity_score?.toFixed(2)} · ${e.github_status}`
                  : e.detail}
              </div>
              <div className="font-mono text-xs text-on-surface-dim">
                {new Date(e.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchRuns, submitIssueUrl, deleteRun } from "../lib/api";

export default function Runs() {
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  function loadRuns() {
    setLoading(true);
    fetchRuns()
      .then((data) => setRuns(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadRuns();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!url) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await submitIssueUrl(url);
      navigate(`/fix-comparison?run_id=${result.run_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(e, runId) {
    e.stopPropagation(); 
    setDeletingId(runId);
    try {
      await deleteRun(runId);
      setRuns((prev) => prev.filter((r) => r.run_id !== runId));
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="p-12">
      <div className="mb-12">
        <div className="font-mono text-xs tracking-widest text-primary mb-3">
          NEW EVALUATION
        </div>
        <h1 className="font-display font-bold text-4xl text-on-surface mb-6">
          Paste a GitHub Issue
        </h1>
        <form onSubmit={handleSubmit} className="flex gap-3 max-w-2xl">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repo/issues/123"
            className="flex-1 bg-surface-low border border-outline px-4 py-3 font-mono text-sm text-on-surface focus:border-outline-active focus:outline-none"
          />
          <button
            type="submit"
            disabled={submitting}
            className="bg-primary text-background font-mono text-xs tracking-widest px-6 py-3 font-bold disabled:opacity-50"
          >
            {submitting ? "RUNNING..." : "RUN PIPELINE"}
          </button>
        </form>
        {error && (
          <div className="font-mono text-xs text-primary mt-3">{error}</div>
        )}
      </div>

      <div>
        <div className="font-mono text-xs tracking-widest text-on-surface-muted mb-4">
          RUN HISTORY
        </div>
        {loading ? (
          <div className="font-mono text-sm text-on-surface-muted">
            Loading...
          </div>
        ) : runs.length === 0 ? (
          <div className="font-mono text-sm text-on-surface-muted border border-outline p-8 text-center">
            No runs yet. Paste an issue URL above to start one.
          </div>
        ) : (
          <div className="border border-outline">
            {runs.map((run) => (
              <div
                key={run.run_id}
                onClick={() => navigate(`/fix-comparison?run_id=${run.run_id}`)}
                className="flex justify-between items-center px-4 py-3 border-b border-outline last:border-b-0 hover:bg-surface-mid cursor-pointer"
              >
                <span className="font-mono text-sm text-on-surface">
                  {run.run_name}
                </span>
                <span
                  className={`font-mono text-xs px-2 py-1 ${
                    run.verdict === "trustworthy"
                      ? "text-trustworthy"
                      : "text-primary"
                  }`}
                >
                  {run.verdict?.toUpperCase() || "PENDING"}
                </span>
                <span className="font-mono text-xs text-on-surface-dim">
                  {run.created_at}
                </span>
                <button
                  onClick={(e) => handleDelete(e, run.run_id)}
                  disabled={deletingId === run.run_id}
                  className="font-mono text-xs text-on-surface-dim hover:text-primary px-2 disabled:opacity-50"
                  title="Delete run"
                >
                  {deletingId === run.run_id ? "..." : "✕"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
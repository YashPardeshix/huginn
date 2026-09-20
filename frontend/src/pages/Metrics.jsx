import { useState, useEffect } from "react";
import { fetchMetricsTrend } from "../lib/api";

export default function Metrics() {
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMetricsTrend()
      .then((data) => setTrend(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const avgScore =
    trend.length > 0
      ? (
          trend.reduce((sum, r) => sum + r.similarity_score, 0) / trend.length
        ).toFixed(2)
      : "—";

  return (
    <div className="p-12">
      <div className="font-mono text-xs tracking-widest text-primary mb-3">
        METRICS
      </div>
      <h1 className="font-display font-bold text-4xl text-on-surface mb-10">
        Trend Over Time
      </h1>

      <div className="grid grid-cols-3 gap-6 mb-12">
        <div className="border border-outline p-6">
          <div className="font-mono text-xs tracking-widest text-on-surface-muted mb-2">
            TOTAL RUNS
          </div>
          <div className="font-display font-bold text-4xl text-on-surface">
            {trend.length}
          </div>
        </div>
        <div className="border border-outline p-6">
          <div className="font-mono text-xs tracking-widest text-on-surface-muted mb-2">
            AVG SIMILARITY
          </div>
          <div className="font-display font-bold text-4xl text-primary">
            {avgScore}
          </div>
        </div>
        <div className="border border-outline p-6">
          <div className="font-mono text-xs tracking-widest text-on-surface-muted mb-2">
            TRUSTWORTHY RATE
          </div>
          <div className="font-display font-bold text-4xl text-trustworthy">
            {trend.length > 0
              ? `${Math.round(
                  (trend.filter((r) => r.verdict === "trustworthy").length /
                    trend.length) *
                    100
                )}%`
              : "—"}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="font-mono text-sm text-on-surface-muted">
          Loading...
        </div>
      ) : error ? (
        <div className="font-mono text-sm text-primary">{error}</div>
      ) : trend.length === 0 ? (
        <div className="border border-outline p-8 text-center font-mono text-sm text-on-surface-muted">
          No runs logged yet. Metrics populate automatically after each
          pipeline run via MLflow.
        </div>
      ) : (
        <div className="border border-outline">
          {trend.map((r, i) => (
            <div
              key={i}
              className="flex justify-between px-4 py-3 border-b border-outline last:border-b-0"
            >
              <span className="font-mono text-xs text-on-surface-dim">
                {r.timestamp}
              </span>
              <span className="font-mono text-sm text-on-surface">
                {r.similarity_score.toFixed(2)}
              </span>
              <span
                className={`font-mono text-xs ${
                  r.verdict === "trustworthy"
                    ? "text-trustworthy"
                    : "text-primary"
                }`}
              >
                {r.verdict?.toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

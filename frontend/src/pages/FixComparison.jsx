import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchRun, fetchRunStatus, approveRun, submitHumanFix } from "../lib/api";

function verdictDisplay(verdict) {
  if (verdict === "trustworthy") {
    return { label: "TRUSTWORTHY", colorClass: "text-trustworthy" };
  }
  if (verdict === "no_human_baseline_yet") {
    return { label: "NO HUMAN BASELINE YET", colorClass: "text-on-surface-muted" };
  }
  return { label: "NEEDS HUMAN REWORK", colorClass: "text-primary" };
}

function VerdictLabel({ verdict }) {
  const { label, colorClass } = verdictDisplay(verdict);
  return (
    <h1 className={`font-display font-bold text-6xl leading-tight ${colorClass}`}>
      {label}
    </h1>
  );
}

function SimilarityScore({ score, verdict }) {
  const { colorClass } = verdictDisplay(verdict);
  return (
    <div className="text-right">
      <div className="font-mono text-xs tracking-widest text-primary mb-2">
        SIMILARITY SCORE [0.00 – 1.00]
      </div>
      <div className={`font-display font-bold text-7xl ${colorClass}`}>
        {score.toFixed(2)}
      </div>
    </div>
  );
}

function CodePane({ label, code, accentClass }) {
  return (
    <div className="border border-outline bg-surface-low flex-1 min-w-[320px]">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-outline">
        <span className={`w-2 h-2 inline-block ${accentClass}`} />
        <span className="font-mono text-xs tracking-widest text-on-surface">
          {label}
        </span>
      </div>
      <pre className="font-mono text-xs leading-relaxed text-on-surface p-4 whitespace-pre-wrap overflow-x-auto">
        {code}
      </pre>
    </div>
  );
}

const NODE_LABELS = {
  starting: "Starting pipeline...",
  triage: "Triage Agent — classifying bug...",
  reproduction: "Reproduction Agent — running in Docker sandbox...",
  diagnosis: "Diagnosis Agent — finding root cause...",
  fix: "Fix Agent — proposing fix...",
  test: "Test Agent — verifying fix in sandbox...",
  shadow_eval: "Shadow Mode Evaluation — comparing to human fix...",
  awaiting_approval: "Paused — awaiting human approval",
  error: "Pipeline failed",
};

function ProgressTracker({ status }) {
  if (!status || !status.current_node) {
    return (
      <div className="p-12 font-mono text-sm text-on-surface-muted">
        Connecting...
      </div>
    );
  }
  const label = NODE_LABELS[status.current_node] || `Running: ${status.current_node}`;
  return (
    <div className="p-12 font-mono text-sm text-on-surface-muted">
      <div className="text-primary mb-2">{label}</div>
      {status.error && (
        <div className="text-primary mt-4">Error: {status.error}</div>
      )}
    </div>
  );
}

function HumanFixForm({ runId, currentFix, lastResult, onSubmitted }) {
  const [isOpen, setIsOpen] = useState(false);
  const [fixText, setFixText] = useState(currentFix || "");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  function handleOpen() {
    setFixText(currentFix || "");
    setFormError(null);
    setIsOpen(true);
  }

  function handleClose() {
    setIsOpen(false);
    setFormError(null);
  }

  async function handleSubmit() {
    if (!fixText.trim()) return;
    setSubmitting(true);
    setFormError(null);
    try {
      await submitHumanFix(runId, fixText);
      onSubmitted();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!isOpen) {
    return (
      <div className="mt-4">
        <button
          onClick={handleOpen}
          className="border border-outline text-on-surface font-mono text-xs tracking-widest px-6 py-3 font-bold hover:border-on-surface"
        >
          {currentFix ? "EDIT HUMAN FIX & RE-EVALUATE" : "SUBMIT HUMAN FIX"}
        </button>
      </div>
    );
  }

  return (
    <div className="border border-outline bg-surface-low p-6 mt-4">
      <div className="flex justify-between items-start mb-3">
        <div className="font-mono text-xs tracking-widest text-primary">
          {currentFix ? "EDIT HUMAN FIX & RE-EVALUATE" : "SUBMIT HUMAN FIX"}
        </div>
        <button
          onClick={handleClose}
          className="font-mono text-xs text-on-surface-dim hover:text-primary px-2"
          title="Close"
        >
          ✕
        </button>
      </div>
      <p className="font-body text-sm text-on-surface-muted mb-4 max-w-2xl">
        {currentFix
          ? "Revise the human fix below and re-run Shadow Mode Evaluation against the updated version."
          : "Paste the real, independently-written fix a human used to resolve this same issue. This will re-run Shadow Mode Evaluation against it."}
      </p>
      <textarea
        value={fixText}
        onChange={(e) => setFixText(e.target.value)}
        placeholder="Paste the human's actual fix code here..."
        rows={8}
        className="w-full bg-background border border-outline font-mono text-xs text-on-surface p-4 focus:outline-none focus:border-on-surface"
      />
      {formError && (
        <div className="font-mono text-xs text-primary mt-2">{formError}</div>
      )}
      {lastResult && (
        <div className="font-mono text-xs text-trustworthy mt-3">
          Last re-evaluation: {lastResult.verdict?.toUpperCase()} — score {lastResult.similarity_score?.toFixed(2)}
        </div>
      )}
      <button
        onClick={handleSubmit}
        disabled={submitting || !fixText.trim()}
        className="bg-primary text-background font-mono text-xs tracking-widest px-6 py-3 font-bold disabled:opacity-50 mt-4"
      >
        {submitting ? "EVALUATING..." : "RE-EVALUATE"}
      </button>
    </div>
  );
}

export default function FixComparison() {
  const [searchParams] = useSearchParams();
  const runId = searchParams.get("run_id");
  const [run, setRun] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [approving, setApproving] = useState(false);
  const pollRef = useRef(null);

  function reloadRun() {
    fetchRun(runId)
      .then((data) => setRun(data))
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    if (!runId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    setRun(null);

    let attempts = 0;
    const MAX_ATTEMPTS = 300; 

    function poll() {
      attempts++;
      if (attempts > MAX_ATTEMPTS) {
        clearInterval(pollRef.current);
        setError(
          "Run status lost — this may be from before a server restart. Please start a new run."
        );
        setLoading(false);
        return;
      }
      fetchRunStatus(runId)
        .then((s) => {
          setStatus(s);
          if (s.error) {
            setError(s.error);
            setLoading(false);
            clearInterval(pollRef.current);
            return;
          }
          if (s.done) {
            clearInterval(pollRef.current);
            fetchRun(runId)
              .then((data) => setRun(data))
              .catch((err) => setError(err.message))
              .finally(() => setLoading(false));
          }
        })
        .catch(() => {
        });
    }

    poll();
    pollRef.current = setInterval(poll, 2000);

    return () => clearInterval(pollRef.current);
  }, [runId]);

  async function handleApprove() {
    setApproving(true);
    try {
      await approveRun(runId);
      const updated = await fetchRun(runId);
      setRun(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setApproving(false);
    }
  }

  if (!runId) {
    return (
      <div className="p-12 font-mono text-sm text-on-surface-muted">
        No run selected. Go to Runs and paste a GitHub issue URL, or click a
        past run.
      </div>
    );
  }

  if (loading) {
    return <ProgressTracker status={status} />;
  }

  if (error) {
    return (
      <div className="p-12 font-mono text-sm text-primary">{error}</div>
    );
  }

  if (!run) {
    return <ProgressTracker status={status} />;
  }

  return (
    <div className="p-12">
      <div className="font-mono text-xs text-primary mb-2">
        EVALUATION ID: #{run.run_id}
      </div>
      <div className="flex justify-between items-start flex-wrap gap-6 mb-12">
        <VerdictLabel verdict={run.verdict} />
        <SimilarityScore score={run.similarity_score} verdict={run.verdict} />
      </div>

      <div className="flex gap-6 flex-wrap">
        <CodePane
          label="AI Proposed Fix"
          code={run.ai_fix}
          accentClass="bg-primary"
        />
        <CodePane
          label="Human's Actual Fix"
          code={run.human_fix || "// Not submitted yet"}
          accentClass="bg-on-surface-muted"
        />
      </div>

      <div className="mt-10">
        <div className="font-mono text-xs tracking-widest text-primary mb-3">
          VERDICT RATIONALE
        </div>
        <p className="font-body text-sm leading-relaxed text-on-surface-muted max-w-2xl">
          {run.reasoning}
        </p>
      </div>

{/* Public Demo Mode: Uncomment below to re-enable human fix editing
      <HumanFixForm
        runId={runId}
        currentFix={run.human_fix}
        lastResult={{ verdict: run.verdict, similarity_score: run.similarity_score }}
        onSubmitted={reloadRun}
      />
*/}
      {run.pending_approval && (
        <div className="mt-10 border-t border-outline pt-8">
          <div className="font-mono text-xs tracking-widest text-on-surface-muted mb-3">
            FINAL DECISION
          </div>
          <p className="font-body text-sm text-on-surface-muted mb-4 max-w-2xl">
            Marks this evaluation as reviewed. Once GitHub posting is wired
            up, this will comment the result on the real issue — and close
            it automatically if the verdict is trustworthy.
          </p>
          <button
            onClick={handleApprove}
            disabled={approving}
            className="bg-primary text-background font-mono text-xs tracking-widest px-6 py-3 font-bold disabled:opacity-50"
          >
            {approving ? "APPROVING..." : "APPROVE & CLOSE OUT"}
          </button>
        </div>
      )}
    </div>
  );
}
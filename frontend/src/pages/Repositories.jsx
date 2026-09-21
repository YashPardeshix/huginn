import { useState, useEffect } from "react";
import { fetchRepositories } from "../lib/api";

export default function Repositories() {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRepositories()
      .then((data) => setRepos(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-12">
      <div className="font-mono text-xs tracking-widest text-primary mb-3">
        REPOSITORIES
      </div>
      <h1 className="font-display font-bold text-4xl text-on-surface mb-6">
        Connected Repos
      </h1>

      {loading ? (
        <div className="font-mono text-sm text-on-surface-muted">
          Loading...
        </div>
      ) : error ? (
        <div className="font-mono text-sm text-primary">{error}</div>
      ) : repos.length === 0 ? (
        <div className="border border-outline p-8 text-center font-mono text-sm text-on-surface-muted">
          No repositories with logged runs yet. Paste a GitHub issue URL or
          trigger the webhook on a connected repo to see it here.
        </div>
      ) : (
        <div className="border border-outline">
          {repos.map((r) => (
            <div
              key={`${r.owner}/${r.repo}`}
              className="flex justify-between items-center px-4 py-3 border-b border-outline last:border-b-0"
            >
              <div>
                <span className="font-mono text-sm text-on-surface">
                  {r.owner}/{r.repo}
                </span>
                <span className="font-mono text-xs text-trustworthy ml-3">
                  ● WEBHOOK ACTIVE
                </span>
              </div>
              <div className="font-mono text-xs text-on-surface-muted">
                {r.run_count} run{r.run_count !== 1 ? "s" : ""} ·{" "}
                {r.trustworthy_count} trustworthy
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
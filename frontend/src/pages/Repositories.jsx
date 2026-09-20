export default function Repositories() {
  return (
    <div className="p-12">
      <div className="font-mono text-xs tracking-widest text-primary mb-3">
        REPOSITORIES
      </div>
      <h1 className="font-display font-bold text-4xl text-on-surface mb-6">
        Connected Repos
      </h1>
      <div className="border border-outline p-8 text-center font-mono text-sm text-on-surface-muted">
        No repositories connected yet. Webhook integration is planned for
        Step 7 of the build (real-world testing on live GitHub issues).
      </div>
    </div>
  );
}

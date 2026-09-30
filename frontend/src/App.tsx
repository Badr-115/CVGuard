import { useEffect, useMemo, useState } from "react";
import { api, register, type Candidate, type Job } from "./api";

type View = "candidates" | "jobs";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const [view, setView] = useState<View>("candidates");
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showCandidate, setShowCandidate] = useState(false);
  const [showJob, setShowJob] = useState(false);

  const refresh = async () => {
    setLoading(true);
    setError("");
    try {
      const [candidateData, jobData] = await Promise.all([
        api<Candidate[]>(`/candidates?search=${encodeURIComponent(search)}`),
        api<Job[]>("/jobs"),
      ]);
      setCandidates(candidateData);
      setJobs(jobData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load workspace");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const expired = () => setToken(null);
    window.addEventListener("auth-expired", expired);
    return () => window.removeEventListener("auth-expired", expired);
  }, []);

  useEffect(() => {
    if (token) refresh();
  }, [token, search]);

  if (!token) {
    return <Auth onLogin={(next) => { localStorage.setItem("access_token", next); setToken(next); }} />;
  }

  const averageScore = useMemo(() => {
    const scored = candidates.filter((candidate) => candidate.score != null);
    return scored.length ? Math.round(scored.reduce((sum, c) => sum + (c.score || 0), 0) / scored.length) : null;
  }, [candidates]);

  function signOut() {
    localStorage.removeItem("access_token");
    setToken(null);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark">CV</div><div><strong>CV Guard</strong><span>Recruit workspace</span></div></div>
        <div className="top-actions"><button className="ghost" onClick={refresh}>Refresh</button><button className="ghost" onClick={signOut}>Sign out</button></div>
      </header>

      <section className="hero">
        <div>
          <span className="eyebrow">Recruiting operations</span>
          <h1>Review candidates with clear evidence.</h1>
          <p>Keep jobs, resumes, and deterministic fit signals in one focused workspace. Scores are matching aids—not hiring decisions.</p>
        </div>
        <button className="primary hero-action" onClick={() => view === "jobs" ? setShowJob(true) : setShowCandidate(true)}>
          {view === "jobs" ? "+ Create job" : "+ Add candidate"}
        </button>
      </section>

      <section className="stats">
        <Stat label="Candidates" value={candidates.length} />
        <Stat label="Open roles" value={jobs.length} />
        <Stat label="Average fit" value={averageScore == null ? "—" : `${averageScore}%`} />
      </section>

      {error && <div className="error" role="alert">{error}</div>}

      <nav className="tabs" aria-label="Workspace sections">
        <button className={view === "candidates" ? "active" : ""} onClick={() => setView("candidates")}>Candidates</button>
        <button className={view === "jobs" ? "active" : ""} onClick={() => setView("jobs")}>Jobs</button>
      </nav>

      <section className="panel">
        <div className="panel-head">
          <div><span className="eyebrow">{view === "candidates" ? "Applicant pipeline" : "Hiring plan"}</span><h2>{view === "candidates" ? "Candidates" : "Jobs"}</h2></div>
          <div className="toolbar">
            {view === "candidates" && <input className="search" aria-label="Search candidates" placeholder="Search candidates…" value={search} onChange={(e) => setSearch(e.target.value)} />}
            <button className="secondary" onClick={() => view === "jobs" ? setShowJob(true) : setShowCandidate(true)}>{view === "jobs" ? "New job" : "New candidate"}</button>
          </div>
        </div>

        {loading ? <div className="empty">Loading workspace…</div> : view === "candidates" ? <CandidateTable candidates={candidates} /> : <JobGrid jobs={jobs} />}
      </section>

      {showCandidate && <CandidateModal jobs={jobs} onClose={() => setShowCandidate(false)} onCreated={refresh} />}
      {showJob && <JobModal onClose={() => setShowJob(false)} onCreated={refresh} />}
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return <div className="stat"><span>{label}</span><strong>{value}</strong></div>;
}

function CandidateTable({ candidates }: { candidates: Candidate[] }) {
  if (!candidates.length) return <div className="empty"><strong>No candidates yet.</strong><span>Add a candidate with a PDF or DOCX resume to start building the pipeline.</span></div>;
  return <div className="table-wrap"><table><thead><tr><th>Candidate</th><th>Contact</th><th>Resume</th><th>Fit signal</th></tr></thead><tbody>
    {candidates.map((candidate) => <tr key={candidate.id}><td><strong>{candidate.name}</strong></td><td>{candidate.email}{candidate.phone && <small>{candidate.phone}</small>}</td><td><span className={`badge ${candidate.resume_uploaded ? "ok" : "muted"}`}>{candidate.resume_uploaded ? "Uploaded" : "Missing"}</span></td><td><Score score={candidate.score} /></td></tr>)}
  </tbody></table></div>;
}

function Score({ score }: { score: number | null }) {
  if (score == null) return <span className="muted-text">Not scored</span>;
  return <div className="score"><span>{score}%</span><div className="meter"><i style={{ width: `${Math.max(0, Math.min(100, score))}%` }} /></div></div>;
}

function JobGrid({ jobs }: { jobs: Job[] }) {
  if (!jobs.length) return <div className="empty"><strong>No jobs yet.</strong><span>Create a role and define the skills used by the matching engine.</span></div>;
  return <div className="job-grid">{jobs.map(job => <article className="job-card" key={job.id}><div><span className="eyebrow">Role #{job.id}</span><h3>{job.title}</h3><p>{job.description}</p></div><div className="chips">{job.required_skills.map(skill => <span key={skill}>{skill}</span>)}</div></article>)}</div>;
}

function Auth({ onLogin }: { onLogin: (token: string) => void }) {
  const [mode, setMode] = useState<"login" | "register">("register");
  const [org, setOrg] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setError(""); setBusy(true);
    try {
      const data = mode === "register"
        ? await register(org, email, password)
        : await api<{ access_token: string }>("/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
      onLogin(data.access_token);
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to authenticate"); }
    finally { setBusy(false); }
  }

  return <main className="auth-shell"><section className="auth-card"><div className="brand auth-brand"><div className="brand-mark">CV</div><div><strong>CV Guard</strong><span>Recruit workspace</span></div></div><span className="eyebrow">Secure workspace</span><h1>{mode === "register" ? "Create your recruiting workspace" : "Welcome back"}</h1><p className="auth-copy">Organize roles and candidate evidence without turning a score into a hiring decision.</p>
    <form onSubmit={submit}>
      {mode === "register" && <label>Organization<input required minLength={2} value={org} onChange={e => setOrg(e.target.value)} placeholder="Acme Inc." /></label>}
      <label>Email<input required type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="email" /></label>
      <label>Password<input required minLength={10} type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 10 characters" autoComplete={mode === "register" ? "new-password" : "current-password"} /></label>
      {error && <div className="error">{error}</div>}
      <button className="primary full" disabled={busy}>{busy ? "Please wait…" : mode === "register" ? "Create workspace" : "Sign in"}</button>
    </form>
    <button className="link" onClick={() => { setMode(mode === "register" ? "login" : "register"); setError(""); }}>{mode === "register" ? "Already have an account? Sign in" : "Create a new workspace"}</button>
  </section></main>;
}

function CandidateModal({ jobs, onClose, onCreated }: { jobs: Job[]; onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState(""); const [email, setEmail] = useState(""); const [phone, setPhone] = useState(""); const [jobId, setJobId] = useState(""); const [file, setFile] = useState<File | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent) { e.preventDefault(); setBusy(true); setError(""); try { const form = new FormData(); form.append("name", name); form.append("email", email); form.append("phone", phone); if (jobId) form.append("job_id", jobId); if (file) form.append("resume", file); await api("/candidates", { method: "POST", body: form }); onCreated(); onClose(); } catch (e) { setError(e instanceof Error ? e.message : "Unable to create candidate"); } finally { setBusy(false); } }
  return <Modal title="Add candidate" onClose={onClose}><form className="modal-form" onSubmit={submit}><label>Name<input required minLength={2} value={name} onChange={e => setName(e.target.value)} /></label><label>Email<input required type="email" value={email} onChange={e => setEmail(e.target.value)} /></label><label>Phone<input value={phone} onChange={e => setPhone(e.target.value)} /></label><label>Role<select value={jobId} onChange={e => setJobId(e.target.value)}><option value="">No role selected</option>{jobs.map(job => <option value={job.id} key={job.id}>{job.title}</option>)}</select></label><label>Resume <small>PDF or DOCX, max 10 MB</small><input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={e => setFile(e.target.files?.[0] || null)} /></label>{error && <div className="error">{error}</div>}<button className="primary full" disabled={busy}>{busy ? "Uploading…" : "Create candidate"}</button></form></Modal>;
}

function JobModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [title, setTitle] = useState(""); const [description, setDescription] = useState(""); const [skills, setSkills] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent) { e.preventDefault(); setBusy(true); setError(""); try { await api("/jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, description, required_skills: skills.split(",").map(x => x.trim()).filter(Boolean) }) }); onCreated(); onClose(); } catch (e) { setError(e instanceof Error ? e.message : "Unable to create job"); } finally { setBusy(false); } }
  return <Modal title="Create job" onClose={onClose}><form className="modal-form" onSubmit={submit}><label>Job title<input required minLength={2} value={title} onChange={e => setTitle(e.target.value)} placeholder="Backend Engineer" /></label><label>Description<textarea required minLength={10} rows={5} value={description} onChange={e => setDescription(e.target.value)} placeholder="What will this person own?" /></label><label>Required skills <small>Comma separated</small><input value={skills} onChange={e => setSkills(e.target.value)} placeholder="Python, PostgreSQL, Docker" /></label>{error && <div className="error">{error}</div>}<button className="primary full" disabled={busy}>{busy ? "Creating…" : "Create job"}</button></form></Modal>;
}

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) { return <div className="modal-backdrop" onMouseDown={onClose}><section className="modal" onMouseDown={e => e.stopPropagation()}><div className="modal-head"><div><span className="eyebrow">Workspace</span><h2>{title}</h2></div><button className="ghost close" onClick={onClose} aria-label="Close">×</button></div>{children}</section></div>; }

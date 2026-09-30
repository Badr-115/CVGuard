const API = (import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");

export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("access_token");
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.dispatchEvent(new Event("auth-expired"));
  }
  if (!response.ok) {
    const message = Array.isArray(data.detail)
      ? data.detail.map((item: { msg?: string }) => item.msg || "Invalid request").join("; ")
      : data.detail || "Request failed";
    throw new Error(message);
  }
  return data;
}

export function register(organization_name: string, email: string, password: string) {
  return api<{ access_token: string }>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ organization_name, email, password }),
  });
}

export type Job = { id: number; title: string; description: string; required_skills: string[] };
export type Candidate = { id: number; name: string; email: string; phone: string; score: number | null; resume_uploaded: boolean };

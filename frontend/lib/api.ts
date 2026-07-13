import { supabase } from "./supabaseClient";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "[http://127.0.0.1:8000](http://127.0.0.1:8000)";

async function authHeader() {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  if (!token) throw new Error("No active session token found");
  return { Authorization: `Bearer ${token}` };
}

export async function searchCompanies(q: string, industry: string | null) {
  const params = new URLSearchParams({ q, ...(industry ? { industry } : {}) });
  const res = await fetch(`${BASE_URL}/companies/search?${params}`, {
    headers: (await authHeader()) as HeadersInit,
  });
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

export async function fetchIndustries() {
  const res = await fetch(`${BASE_URL}/industries`, {
    headers: (await authHeader()) as HeadersInit,
  });
  if (!res.ok) throw new Error("Failed to load industries");
  return res.json();
}

export async function getOrCreateIndustry(name_en: string) {
  const res = await fetch(`${BASE_URL}/industries`, {
    method: "POST",
    headers: { ...(await authHeader()), "Content-Type": "application/json" },
    body: JSON.stringify({ name_en }),
  });
  if (!res.ok) throw new Error("Failed to save industry");
  return res.json();
}

export async function fetchReviewQueue() {
  const res = await fetch(`${BASE_URL}/review-queue`, {
    headers: (await authHeader()) as HeadersInit,
  });
  if (!res.ok) throw new Error("Failed to load review queue");
  return res.json();
}

export async function approveEntry(id: string) {
  const res = await fetch(`${BASE_URL}/review-queue/${id}/approve`, {
    method: "POST",
    headers: (await authHeader()) as HeadersInit,
  });
  if (!res.ok) throw new Error("Approve failed");
}

export async function rejectEntry(id: string) {
  const res = await fetch(`${BASE_URL}/review-queue/${id}/reject`, {
    method: "POST",
    headers: (await authHeader()) as HeadersInit,
  });
  if (!res.ok) throw new Error("Reject failed");
}

export async function createCompany(payload: {
  name: string;
  phones: { number: string; type: string }[];
  address: string;
  industry_id?: string | null;
}) {
  const res = await fetch(`${BASE_URL}/companies`, {
    method: "POST",
    headers: {
      ...((await authHeader()) as any),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Create failed");
  return res.json();
}

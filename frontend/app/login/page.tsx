"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

// app/login/page.tsx — inside handleLogin, just this one line changes
async function handleLogin(e: React.FormEvent) {
  e.preventDefault();
  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) { setError(error.message); return; }
  window.location.href = "/";  // was router.push("/") — hard nav so middleware sees the fresh cookie
}

  return (
    <main className="mx-auto flex min-h-[80vh] max-w-sm flex-col justify-center p-6">
      <h1 className="mb-6 text-xl font-bold text-ink">Sign in</h1>
      <form onSubmit={handleLogin} className="flex flex-col gap-3">
        <input 
          type="email" 
          required 
          placeholder="Email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-lg border border-line bg-white px-4 py-2 text-ink focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/30" 
        />
        <input 
          type="password" 
          required 
          placeholder="Password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-lg border border-line bg-white px-4 py-2 text-ink focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/30" 
        />
        {error && <p className="text-sm text-danger">{error}</p>}
        <button 
          type="submit" 
          className="rounded-lg bg-ink py-2 font-medium text-white hover:bg-ink/90 transition-colors"
        >
          Sign in
        </button>
      </form>
      <p className="mt-4 text-xs text-ink-muted">
        No sign-up — accounts are created by your org admin.
      </p>
    </main>
  );
}
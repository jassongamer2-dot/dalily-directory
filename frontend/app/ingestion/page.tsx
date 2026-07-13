"use client";
import { useState, useRef } from "react";
import { supabase } from "@/lib/supabaseClient";

export default function IngestionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://dalily-directory-production.up.railway.app";

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setStatusMsg("Uploading document...");
    setJobId(null);

    try {
      // 1. Fetch active authentication token from Supabase
      const { data } = await supabase.auth.getSession();
      const token = data.session?.access_token;
      if (!token) throw new Error("No active session token found. Please re-login.");

      // 2. Prepare Multi-part form payload
      const formData = new FormData();
      formData.append("file", file);

      // 3. Post to the FastAPI Ingestion upload endpoint
      const res = await fetch(`${BASE_URL}/ingestion/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status ${res.status}`);
      }

      const jobResult = await res.json();
      setJobId(jobResult.job_id);
      setStatusMsg(`Success! Document queued into pipeline.`);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err: any) {
      console.error(err);
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md p-6 mt-8 rounded-xl border border-line bg-white shadow-sm">
      <h1 className="mb-2 text-xl font-bold text-ink">Document Ingestion Pipeline</h1>
      <p className="mb-6 text-sm text-ink-muted">
        Upload scanned Arabic directory PDFs, Excel sheets, or Word catalogs. The background worker will process the entries automatically.
      </p>

      <form onSubmit={handleUpload} className="flex flex-col gap-4">
        <div className="flex flex-col items-center justify-center border-2 border-dashed border-line rounded-lg p-6 bg-cream hover:bg-zinc-50 transition-colors">
          <input
            type="file"
            ref={fileInputRef}
            accept=".pdf,.xlsx,.xls,.csv,.docx"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="hidden"
            id="directory-file-input"
          />
          <label htmlFor="directory-file-input" className="cursor-pointer text-center flex flex-col items-center">
            <span className="text-sm font-semibold text-ink">
              {file ? "Selected File:" : "Click to choose file"}
            </span>
            <span className="mt-1 text-xs text-ink-muted max-w-[250px] truncate font-mono">
              {file ? file.name : "Supports PDF, Excel, and DOCX"}
            </span>
          </label>
        </div>

        <button
          type="submit"
          disabled={!file || uploading}
          className={`rounded-lg py-2.5 font-medium text-white transition-all ${
            !file || uploading ? "bg-ink-muted opacity-50 cursor-not-allowed" : "bg-ink hover:opacity-90"
          }`}
        >
          {uploading ? "Processing Pipeline..." : "Send to Worker"}
        </button>
      </form>

      {statusMsg && (
        <div className="mt-4 p-3 rounded-lg bg-zinc-50 border border-line text-sm text-ink font-medium">
          <p>{statusMsg}</p>
          {jobId && (
            <p className="mt-1 text-xs text-ink-muted font-mono selection:bg-brass">
              Job ID: {jobId}
            </p>
          )}
        </div>
      )}
    </main>
  );
}
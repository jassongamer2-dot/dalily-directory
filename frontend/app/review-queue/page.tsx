"use client";
import { useEffect, useState } from "react";
import { fetchReviewQueue, approveEntry, rejectEntry } from "@/lib/api";

export default function ReviewQueuePage() {
  const [items, setItems] = useState<{ id: string; name: string; address: string }[]>([]);
  
  useEffect(() => { 
    fetchReviewQueue().then(setItems); 
  }, []);

  async function handle(id: string, action: "approve" | "reject") {
    await (action === "approve" ? approveEntry(id) : rejectEntry(id));
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  return (
    <main className="mx-auto max-w-2xl p-4">
      <h1 className="mb-4 text-lg font-bold text-ink">Review Queue ({items.length})</h1>
      {items.map((item) => (
        <div key={item.id} className="mb-3 rounded-xl border border-line bg-white p-4">
          <p className="font-semibold text-ink" dir="auto">{item.name || "(no name extracted)"}</p>
          <p className="text-sm text-ink-muted" dir="auto">{item.address}</p>
          <div className="mt-3 flex gap-2">
            <button onClick={() => handle(item.id, "approve")}
              className="rounded-lg bg-ink px-3 py-1.5 text-sm font-medium text-white">Approve</button>
            <button onClick={() => handle(item.id, "reject")}
              className="rounded-lg bg-danger px-3 py-1.5 text-sm font-medium text-white">Reject</button>
          </div>
        </div>
      ))}
      {items.length === 0 && <p className="text-ink-muted">Nothing pending review.</p>}
    </main>
  );
}
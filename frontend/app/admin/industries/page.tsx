// frontend/app/admin/industries/page.tsx
"use client";
import { useEffect, useState } from "react";
import { fetchIndustries, renameIndustry, deleteIndustry } from "@/lib/api";

export default function IndustriesAdminPage() {
  const [industries, setIndustries] = useState<{ id: string; name_en: string }[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => { fetchIndustries().then(setIndustries); }, []);

  async function handleRename(id: string) {
    const updated = await renameIndustry(id, editValue.trim());
    setIndustries((prev) => prev.map((i) => (i.id === id ? updated : i)));
    setEditingId(null);
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this industry? Companies using it keep everything else, just lose this tag.")) return;
    await deleteIndustry(id);
    setIndustries((prev) => prev.filter((i) => i.id !== id));
  }

  return (
    <main className="mx-auto max-w-2xl p-4">
      <h1 className="mb-4 text-lg font-bold text-ink">Manage Industries</h1>
      {industries.map((ind) => (
        <div key={ind.id} className="mb-2 flex items-center justify-between rounded-xl border border-line bg-white p-3">
          {editingId === ind.id ? (
            <input autoFocus dir="auto" value={editValue} onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleRename(ind.id)}
              className="flex-1 rounded border border-line px-2 py-1 text-ink" />
          ) : (
            <span className="text-ink" dir="auto">{ind.name_en}</span>
          )}
          <div className="flex gap-2">
            {editingId === ind.id ? (
              <button onClick={() => handleRename(ind.id)} className="rounded bg-ink px-2 py-1 text-xs text-white">Save</button>
            ) : (
              <button onClick={() => { setEditingId(ind.id); setEditValue(ind.name_en); }}
                className="rounded border border-line px-2 py-1 text-xs text-ink-muted">Rename</button>
            )}
            <button onClick={() => handleDelete(ind.id)} className="rounded bg-danger px-2 py-1 text-xs text-white">Delete</button>
          </div>
        </div>
      ))}
    </main>
  );
}
import { useEffect, useState } from "react";
import { fetchIndustries } from "@/lib/api";

export default function IndustryFilter({ value, onChange }: { value: string | null; onChange: (v: string | null) => void }) {
  const [industries, setIndustries] = useState<{id: string, name_en: string}[]>([]);
  useEffect(() => { fetchIndustries().then(setIndustries); }, []);

  return (
    <div className="mt-2 flex flex-wrap gap-2">
      <button onClick={() => onChange(null)}
        className={`rounded-full px-3 py-1 text-sm ${!value ? "bg-ink text-white" : "border border-line bg-white text-ink-muted"}`}>
        All
      </button>
      {industries.map((ind) => (
        <button key={ind.id} onClick={() => onChange(ind.id)}
          className={`rounded-full px-3 py-1 text-sm ${value === ind.id ? "bg-brass text-white" : "border border-line bg-white text-ink-muted"}`}>
          {ind.name_en}
        </button>
      ))}
    </div>
  );
}
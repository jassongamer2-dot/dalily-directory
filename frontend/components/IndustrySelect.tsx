import { useEffect, useState } from "react";
import { fetchIndustries, getOrCreateIndustry } from "@/lib/api";

export default function IndustrySelect({ value, onChange }: { value: string | null; onChange: (id: string) => void }) {
    const [industries, setIndustries] = useState<{ id: string; name_en: string }[]>([]);
    const [adding, setAdding] = useState(false);
    const [newName, setNewName] = useState("");

    useEffect(() => { fetchIndustries().then(setIndustries); }, []);

    async function handleCreate() {
        const trimmed = newName.trim();
        if (!trimmed) return;
        const industry = await getOrCreateIndustry(trimmed); 
        setIndustries((prev) => (prev.some((i) => i.id === industry.id) ? prev : [...prev, industry]));
        onChange(industry.id);
        setAdding(false);
        setNewName("");
    }

    if (adding) {
        return (
            <div className="flex gap-2">
                <input autoFocus dir="auto" placeholder="New industry name" value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleCreate())}
                    className="flex-1 rounded-lg border border-line bg-white px-4 py-2 text-ink" />
                <button type="button" onClick={handleCreate} className="rounded-lg bg-ink px-3 py-2 text-sm font-medium text-white">Add</button>
                <button type="button" onClick={() => setAdding(false)} className="rounded-lg border border-line px-3 py-2 text-sm text-ink-muted">Cancel</button>
            </div>
        );
    }

    return (
        <select value={value ?? ""} onChange={(e) => (e.target.value === "__new__" ? setAdding(true) : onChange(e.target.value))}
            className="w-full rounded-lg border border-line bg-white px-4 py-2 text-ink">
            <option value="" disabled>Select an industry</option>
            {industries.map((ind) => <option key={ind.id} value={ind.id}>{ind.name_en}</option>)}
            <option value="__new__">+ Add new industry…</option>
        </select>
    );
}
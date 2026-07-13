"use client";
import { useState } from "react";
import { createCompany } from "@/lib/api";
import IndustrySelect from "@/components/IndustrySelect";

export default function ManualEntryPage() {
    const [form, setForm] = useState({ name: "", phone: "", address: "", industry_id: null as string | null });
    const [saved, setSaved] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        await createCompany({
            name: form.name,
            phones: form.phone ? [{ number: form.phone, type: "unspecified" }] : [],
            address: form.address,
            industry_id: form.industry_id,
        });
        setForm({ name: "", phone: "", address: "", industry_id: null });
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    }

    return (
        <main className="mx-auto max-w-md p-4">
            <h1 className="mb-4 text-lg font-bold text-ink">Add a company</h1>
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
                <input required placeholder="Company name" dir="auto" value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="rounded-lg border border-line bg-white px-4 py-2 text-ink" />
                <IndustrySelect value={form.industry_id} onChange={(id) => setForm({ ...form, industry_id: id })} />
                <input placeholder="Phone number" value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    className="rounded-lg border border-line bg-white px-4 py-2 font-mono text-ink" />
                <input placeholder="Address" dir="auto" value={form.address}
                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                    className="rounded-lg border border-line bg-white px-4 py-2 text-ink" />
                <button type="submit" className="rounded-lg bg-ink py-2 font-medium text-white">Save</button>
                {saved && <p className="text-sm text-brass">Saved — verified immediately.</p>}
            </form>
        </main>
    );
}
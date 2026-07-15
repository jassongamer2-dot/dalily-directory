"use client";
import { useState, useEffect } from "react";
import { useDebouncedValue } from "@/lib/useDebouncedValue";
import { searchCompanies } from "@/lib/api";
import CompanyCard from "@/components/CompanyCard";
import SearchBar from "@/components/SearchBar";
import IndustryFilter from "@/components/IndustryFilter";

export default function DirectoryPage() {
  const [query, setQuery] = useState("");
  const [industry, setIndustry] = useState<string | null>(null);
  const debouncedQuery = useDebouncedValue(query, 300);
  const [results, setResults] = useState<{results: any[]}>({ results: [] });

  // app/page.tsx — the effect, remove the early-return guard
  useEffect(() => {
  searchCompanies(debouncedQuery, industry).then(setResults);
}, [debouncedQuery, industry]);

  return (
    <main className="mx-auto max-w-2xl p-4">
      <SearchBar value={query} onChange={setQuery} />
      <IndustryFilter value={industry} onChange={setIndustry} />
      <div className="mt-4 flex flex-col gap-3">
        {results.results.map((c: any) => <CompanyCard key={c.id} company={c} />)}
      </div>
    </main>
  );
}
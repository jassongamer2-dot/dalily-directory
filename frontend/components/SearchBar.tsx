export default function SearchBar({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <input
      type="search"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Search by company name..."
      dir="auto"
      className="w-full rounded-lg border border-line bg-white px-4 py-3 text-base text-ink placeholder:text-ink-muted focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/30"
    />
  );
}
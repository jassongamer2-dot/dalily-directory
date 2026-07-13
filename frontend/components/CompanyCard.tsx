import ContactButtons from "./ContactButtons";

export default function CompanyCard({ company }: { company: any }) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-line bg-white pl-6 shadow-sm">
      {company.industry_name && (
        <span className="absolute left-0 top-0 flex h-full w-6 items-center justify-center border-r border-line bg-paper">
          <span className="origin-center -rotate-90 whitespace-nowrap text-[10px] font-semibold uppercase tracking-wide text-brass">
            {company.industry_name}
          </span>
        </span>
      )}
      <div className="p-4">
        <h3 className="font-semibold text-ink" dir="auto">{company.name}</h3>
        {company.address && <p className="text-sm text-ink-muted" dir="auto">{company.address}</p>}
        <div className="mt-3"><ContactButtons phones={company.phones} /></div>
      </div>
    </div>
  );
}
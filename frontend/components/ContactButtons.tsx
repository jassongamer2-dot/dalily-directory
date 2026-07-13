function toInternational(localNumber: string) {
  return `+20${localNumber.replace(/^0/, "")}`;
}

export default function ContactButtons({ phones }: { phones: any[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {phones.map((phone) => {
        const intl = toInternational(phone.number);
        return (
          <div key={phone.number} className="flex gap-1.5">
            <a href={`tel:${intl}`}
               className="flex items-center gap-1.5 rounded-lg bg-ink px-3 py-2 font-mono text-sm text-white">
              Call · {phone.number}
            </a>
            {phone.type === "mobile" && (
              <a href={`https://wa.me/${intl.replace("+", "")}`} target="_blank" rel="noopener noreferrer"
                 className="rounded-lg bg-whatsapp px-3 py-2 text-sm font-medium text-white">
                WhatsApp
              </a>
            )}
          </div>
        );
      })}
    </div>
  );
}
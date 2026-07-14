import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "Dalily — Industrial Directory",
  manifest: "/manifest.json",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-paper text-ink font-sans min-h-screen flex flex-col">
        
        {/* Top Navigation Bar */}
        <header className="border-b border-line px-6 py-4 bg-white shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-8">
            <span className="text-xl font-bold tracking-tight text-brass">Dalily</span>
            
            <nav className="flex gap-6">
              <Link href="/" className="text-sm font-semibold text-ink-muted hover:text-brass transition-colors">
                Search Directory
              </Link>
              <Link href="/manual-entry" className="text-sm font-semibold text-ink-muted hover:text-brass transition-colors">
                Add Company
              </Link>
              <Link href="/review-queue" className="text-sm font-semibold text-ink-muted hover:text-brass transition-colors">
                Review Queue
              </Link>
              <Link href="/ingestion" className="text-sm font-semibold text-ink-muted hover:text-brass transition-colors">
                Upload Documents
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Page Content */}
        <div className="flex-1 w-full max-w-4xl mx-auto mt-6">
          {children}
        </div>

      </body>
    </html>
  );
}
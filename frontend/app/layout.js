import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "Hybrid Computing Analyzer",
  description: "Thread + ProcessPool and MPI Analysis Tool",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50 min-h-screen">
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link href="/">
                  <h1 className="text-2xl font-bold text-gray-900 cursor-pointer">
                    🚀 Hybrid Computing Analyzer
                  </h1>
                </Link>
              </div>
              <div className="flex items-center space-x-4">
                <Link href="/" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Home
                </Link>
                <Link href="/thread-process" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  Thread + Process
                </Link>
                <Link href="/mpi" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  MPI
                </Link>
                <Link href="/comparison" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                  📊 Comparison
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}

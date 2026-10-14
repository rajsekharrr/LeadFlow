export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            LeadFlow
          </h1>
          <p className="text-gray-600 mt-2">
            Lead Management System
          </p>
        </header>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Frontend Scaffold Ready
          </h2>
          <p className="text-gray-600 mb-4">
            Next.js 14 with App Router, TypeScript, and Tailwind CSS is configured.
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-2">
            <li>Next.js 14 App Router</li>
            <li>TypeScript for type safety</li>
            <li>Tailwind CSS for styling</li>
            <li>Axios for API calls</li>
            <li>date-fns for date formatting</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

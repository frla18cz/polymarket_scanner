import SummaryTable from "@/components/SummaryTable";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 p-8 text-black">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Polymarket Equity Dashboard</h1>
          <p className="text-gray-500">Analyze user performance, equity curves, and risk metrics.</p>
        </div>
        
        <SummaryTable />
      </div>
    </main>
  );
}
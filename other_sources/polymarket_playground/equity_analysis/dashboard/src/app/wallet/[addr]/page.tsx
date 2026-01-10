import WalletDetail from "@/components/WalletDetail";

export default async function WalletPage({ params }: { params: Promise<{ addr: string }> }) {
  const { addr } = await params;

  return (
    <main className="min-h-screen bg-gray-50 p-8 text-black">
      <div className="max-w-7xl mx-auto">
        <WalletDetail addr={addr} />
      </div>
    </main>
  );
}

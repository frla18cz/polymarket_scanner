import { NextRequest, NextResponse } from 'next/server';
import { getWalletData } from '@/lib/data';

export async function GET(request: NextRequest, { params }: { params: Promise<{ addr: string }> }) {
  const { addr } = await params;

  const { searchParams } = new URL(request.url);
  const resample = (searchParams.get('resample') as 'H' | 'D' | 'raw') || 'raw';

  const data = await getWalletData(addr, resample);
  return NextResponse.json(data);
}

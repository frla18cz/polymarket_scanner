import { NextResponse } from 'next/server';
import { getScoresWithIndex } from '@/lib/data';

const VALID_SORT = new Set([
  'score',
  'smoothness',
  'sharpe',
  'max_drawdown',
  'net_change',
  'equity_end',
  'points',
]);

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limitParam = searchParams.get('limit');
  const limit = limitParam === 'all' ? -1 : parseInt(limitParam || '20');
  const minPoints = parseInt(searchParams.get('minPoints') || '10');
  const minScore = parseFloat(searchParams.get('minScore') || '-999');
  const minProfit = parseFloat(searchParams.get('minProfit') || '0');
  const search = (searchParams.get('search') || '').toLowerCase().trim();
  const sortBy = VALID_SORT.has(searchParams.get('sortBy') || '') ? (searchParams.get('sortBy') as string) : 'score';
  const sortDir = (searchParams.get('sortDir') || 'desc').toLowerCase() === 'asc' ? 'asc' : 'desc';

  const { scores, index } = await getScoresWithIndex();
  const term = search.trim();

  if (term) {
    const exact = index.get(term);
    if (exact) {
      return NextResponse.json([exact]);
    }
  }

  let filtered = scores;

  filtered = filtered.filter(
    (s) =>
      s.points >= minPoints &&
      s.score >= minScore &&
      s.net_change >= minProfit,
  );

  if (term) {
    filtered = filtered.filter((s) => s.wallet.toLowerCase().includes(term));
  }

  filtered.sort((a, b) => {
    const av = (a as Record<string, number | string>)[sortBy];
    const bv = (b as Record<string, number | string>)[sortBy];
    if (av === bv) return 0;
    return sortDir === 'asc' ? (av < bv ? -1 : 1) : av > bv ? -1 : 1;
  });

  if (limit > 0) {
    filtered = filtered.slice(0, limit);
  }

  return NextResponse.json(filtered);
}

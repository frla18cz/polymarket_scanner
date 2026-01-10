"use client";

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { EquityScore } from '@/lib/types';
import { Search } from 'lucide-react';
import { twMerge } from 'tailwind-merge';

const STORAGE_KEY = 'equity-dashboard-filters';

type SortKey = keyof EquityScore;
const DEFAULT_LIMIT = 20;
const LIMIT_OPTIONS = [20, 200, 500, -1]; // -1 = All

export default function SummaryTable() {
  const router = useRouter();
  const [scores, setScores] = useState<EquityScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [pendingSearch, setPendingSearch] = useState('');
  const [refreshTick, setRefreshTick] = useState(0);
  const [minPoints, setMinPoints] = useState(10);
  const [minScore, setMinScore] = useState(-5); // Default loose filter
  const [minProfit, setMinProfit] = useState(5000); // USD net_change filter
  const [sortKey, setSortKey] = useState<SortKey>('score');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [limit, setLimit] = useState<number>(DEFAULT_LIMIT);

  // Load saved filters from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      const saved = JSON.parse(raw);
      if (saved.search) setPendingSearch(saved.search);
      if (saved.minPoints !== undefined) setMinPoints(Number(saved.minPoints));
      if (saved.minScore !== undefined) setMinScore(Number(saved.minScore));
      if (saved.minProfit !== undefined) setMinProfit(Number(saved.minProfit));
      if (saved.sortKey) setSortKey(saved.sortKey);
      if (saved.sortDir) setSortDir(saved.sortDir);
      if (saved.limit !== undefined) setLimit(Number(saved.limit));
    } catch (e) {
      console.warn('Cannot parse saved filters', e);
    }
  }, []);

  // Persist filters to localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const payload = {
      search: pendingSearch,
      minPoints,
      minScore,
      minProfit,
      sortKey,
      sortDir,
      limit,
    };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, [pendingSearch, minPoints, minScore, minProfit, sortKey, sortDir, limit]);

  const fetchScores = useCallback(async () => {
    setLoading(true);
    try {
      const limitParam = limit === -1 ? 'all' : limit;
      const res = await fetch(
        `/api/scores?minPoints=${minPoints}&minScore=${minScore}&minProfit=${minProfit}&limit=${limitParam}&sortBy=${sortKey}&sortDir=${sortDir}&search=${encodeURIComponent(search)}`,
      );
      const data = await res.json();
      setScores(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [minPoints, minScore, minProfit, sortKey, sortDir, limit, search]);

  useEffect(() => {
    fetchScores();
  }, [fetchScores, refreshTick]);

  const filteredScores = scores; // server-side search/filter already applied

  const applySearch = () => {
    setSearch(pendingSearch.trim());
    setRefreshTick((t) => t + 1);
  };

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row gap-4 justify-between items-end md:items-center bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search wallet address..."
            className="pl-9 h-10 w-full min-w-[220px] rounded-md border border-gray-200 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
            value={pendingSearch}
            onChange={(e) => setPendingSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                applySearch();
              }
            }}
          />
        </div>
        <div className="flex gap-4 items-center">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Min Trades:</span>
            <input 
              type="number" 
              value={minPoints} 
              onChange={e => setMinPoints(Number(e.target.value))}
              className="w-16 h-9 rounded-md border border-gray-200 px-2 text-sm text-black"
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Min Score:</span>
            <input 
              type="number" 
              value={minScore} 
              onChange={e => setMinScore(Number(e.target.value))}
              className="w-16 h-9 rounded-md border border-gray-200 px-2 text-sm text-black"
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Min Profit:</span>
            <input
              type="number"
              value={minProfit}
              onChange={(e) => setMinProfit(Number(e.target.value))}
              className="w-24 h-9 rounded-md border border-gray-200 px-2 text-sm text-black"
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Limit:</span>
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="h-9 rounded-md border border-gray-200 px-2 text-sm text-black"
            >
              {LIMIT_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt === -1 ? 'All' : opt}
                </option>
              ))}
            </select>
          </div>
          <button 
            onClick={applySearch}
            className="h-9 px-4 rounded-md bg-blue-600 text-white text-sm hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="rounded-md border border-gray-200 bg-white overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-4 py-3 font-medium cursor-pointer" onClick={() => toggleSort('wallet')}>Wallet</th>
                <th className="px-4 py-3 font-medium text-right cursor-pointer" onClick={() => toggleSort('score')}>Score</th>
                <th className="px-4 py-3 font-medium text-right cursor-pointer" onClick={() => toggleSort('smoothness')}>Smoothness</th>
                <th className="px-4 py-3 font-medium text-right cursor-pointer" onClick={() => toggleSort('sharpe')}>Sharpe</th>
                <th className="px-4 py-3 font-medium text-right cursor-pointer" onClick={() => toggleSort('max_drawdown')}>Max DD</th>
                <th className="px-4 py-3 font-medium text-right cursor-pointer" onClick={() => toggleSort('equity_end')}>Equity End</th>
                <th className="px-4 py-3 font-medium text-right cursor-pointer" onClick={() => toggleSort('points')}>Trades</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">Loading data...</td>
                </tr>
              ) : filteredScores.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">No wallets found matching criteria.</td>
                </tr>
              ) : (
                filteredScores.map((row) => (
                  <tr 
                    key={row.wallet} 
                    onClick={() => router.push(`/wallet/${row.wallet}`)}
                    className="hover:bg-blue-50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-gray-700">{row.wallet}</td>
                    <td className={twMerge("px-4 py-3 text-right font-medium", row.score > 0 ? "text-green-600" : "text-red-600")}>
                      {row.score.toFixed(3)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">{row.smoothness.toFixed(3)}</td>
                    <td className="px-4 py-3 text-right text-gray-600">{row.sharpe.toFixed(3)}</td>
                    <td className="px-4 py-3 text-right text-red-500">{row.max_drawdown.toFixed(3)}</td>
                    <td className="px-4 py-3 text-right text-gray-700">{row.equity_end.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right text-gray-500">{row.points}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

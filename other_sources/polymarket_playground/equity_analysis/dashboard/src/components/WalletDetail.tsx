"use client";

import { useEffect, useState, useMemo, useCallback } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { WalletTimeSeriesPoint } from '@/lib/types';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface WalletDetailProps {
  addr: string;
}

export default function WalletDetail({ addr }: WalletDetailProps) {
  const router = useRouter();
  const [data, setData] = useState<WalletTimeSeriesPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [resample, setResample] = useState<'raw' | 'H' | 'D'>('raw');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/wallet/${addr}?resample=${resample}`);
      const points = await res.json();
      setData(points);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [addr, resample]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const stats = useMemo(() => {
    if (data.length === 0) return null;
    const start = data[0].equity;
    const end = data[data.length - 1].equity;
    const net = end - start;
    const min = Math.min(...data.map(d => d.equity));
    const max = Math.max(...data.map(d => d.equity));
    return { start, end, net, min, max, count: data.length };
  }, [data]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => router.back()}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 font-mono">{addr}</h1>
          <p className="text-sm text-gray-500">Equity Curve Analysis</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <p className="text-xs text-gray-500 uppercase font-medium">Net PnL</p>
          <p className={`text-2xl font-bold ${stats && stats.net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {stats ? stats.net.toFixed(2) : '-'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <p className="text-xs text-gray-500 uppercase font-medium">Current Equity</p>
          <p className="text-2xl font-bold text-gray-900">
            {stats ? stats.end.toFixed(2) : '-'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <p className="text-xs text-gray-500 uppercase font-medium">Min / Max</p>
          <p className="text-lg font-medium text-gray-700">
            {stats ? `${stats.min.toFixed(0)} / ${stats.max.toFixed(0)}` : '-'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-center gap-2">
           <p className="text-xs text-gray-500 uppercase font-medium">Resampling</p>
           <div className="flex bg-gray-100 rounded-md p-1">
             {(['raw', 'H', 'D'] as const).map((r) => (
               <button
                 key={r}
                 onClick={() => setResample(r)}
                 className={`flex-1 text-xs py-1 rounded-sm transition-all ${resample === r ? 'bg-white shadow-sm font-medium text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
               >
                 {r === 'raw' ? 'Raw' : r === 'H' ? 'Hour' : 'Day'}
               </button>
             ))}
           </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm h-[500px]">
        {loading ? (
          <div className="h-full flex items-center justify-center text-gray-400">Loading chart data...</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={(val) => new Date(val).toLocaleDateString()}
                minTickGap={50}
                tick={{fontSize: 12, fill: '#888'}}
              />
              <YAxis 
                domain={['auto', 'auto']}
                tick={{fontSize: 12, fill: '#888'}}
                tickFormatter={(val) => val.toFixed(0)}
              />
              <Tooltip 
                contentStyle={{backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #eee', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                labelFormatter={(val) => new Date(val).toLocaleString()}
                formatter={(val: number, name: string) => {
                  if (name === 'equity') {
                    return [val.toFixed(2), 'Equity'];
                  }
                  if (name === 'pnl_delta') {
                    return [val.toFixed(2), 'ΔPnL'];
                  }
                  return [val.toFixed(2), name];
                }}
              />
              <ReferenceLine y={0} stroke="#000" strokeOpacity={0.1} />
              <Line 
                type="monotone" 
                dataKey="equity" 
                stroke="#2563eb" 
                strokeWidth={2} 
                dot={false} 
                activeDot={{r: 4}}
              />
              <Line 
                type="monotone"
                dataKey="pnl_delta"
                stroke="#9ca3af"
                strokeWidth={1}
                dot={false}
                strokeDasharray="4 4"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

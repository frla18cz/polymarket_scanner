import fs from 'fs';
import { parse } from 'csv-parse/sync';
import { SCORES_CSV_PATH } from './config';
import { query } from './db';
import { EquityScore, WalletTimeSeriesPoint } from './types';

let cachedScores: EquityScore[] | null = null;
let cachedMtimeMs: number | null = null;
let cachedIndex: Map<string, EquityScore> | null = null;

export async function getScores(): Promise<EquityScore[]> {
  if (!fs.existsSync(SCORES_CSV_PATH)) {
    console.warn(`CSV file not found at ${SCORES_CSV_PATH}`);
    return [];
  }

  try {
    const stat = fs.statSync(SCORES_CSV_PATH);
    const mtimeMs = stat.mtimeMs;
    if (cachedScores && cachedMtimeMs === mtimeMs) {
      return cachedScores;
    }

    const fileContent = fs.readFileSync(SCORES_CSV_PATH, 'utf-8');
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
      cast: (value, context) => {
        if (context.column === 'wallet') return value;
        const num = Number(value);
        return isNaN(num) ? value : num;
      }
    });
    cachedScores = records as EquityScore[];
    cachedMtimeMs = mtimeMs;
    cachedIndex = null; // invalidate index
    return cachedScores;
  } catch (error) {
    console.error('Error reading scores CSV:', error);
    return [];
  }
}

export async function getScoresWithIndex(): Promise<{ scores: EquityScore[]; index: Map<string, EquityScore> }> {
  const scores = await getScores();
  if (!cachedIndex) {
    cachedIndex = new Map(scores.map((s) => [s.wallet.toLowerCase(), s]));
  }
  return { scores, index: cachedIndex };
}

export async function getWalletData(addr: string, resample: 'H' | 'D' | 'raw' = 'raw'): Promise<WalletTimeSeriesPoint[]> {
  console.log(`Querying wallet data for: ${addr} (resample: ${resample})`);
  const isBucketed = resample !== 'raw';
  const timeExpr = resample === 'H' ? "date_trunc('hour', updated_at)" :
                   resample === 'D' ? "date_trunc('day', updated_at)" :
                   "updated_at";
  const valueExpr = isBucketed ? "SUM(realizedPnl)/1e6" : "realizedPnl/1e6";
  const groupBy = isBucketed ? 'GROUP BY 1' : '';

  const sql = `
    SELECT ${timeExpr} as timestamp, ${valueExpr} as pnl_delta
    FROM user_positions
    WHERE lower(user_addr) = lower(?)
    ${groupBy}
    ORDER BY timestamp ASC
  `;

  try {
    type Row = { timestamp: string | Date; pnl_delta: number | null };
    const rows = await query<Row>(sql, [addr]);
    console.log(`Found ${rows.length} rows for ${addr}`);

    if (!rows.length) return [];

    // Build cumulative equity from PnL deltas
    let equity = 0;
    const series: WalletTimeSeriesPoint[] = [];
    const sorted = rows
      .map((r) => ({
        timestamp: new Date(r.timestamp),
        pnl_delta: Number(r.pnl_delta ?? 0),
      }))
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
      .map((row, idx) => ({
        ...row,
        // Pokud jsou všechny timestampy stejné, posuňme je o index v ms, aby graf nebyl degenerovaný.
        timestamp: new Date(row.timestamp.getTime() + idx),
      }));

    // Start from zero equity baseline
    series.push({
      timestamp: sorted[0].timestamp.toISOString(),
      pnl_delta: 0,
      equity: 0,
    });

    for (const row of sorted) {
      equity += row.pnl_delta;
      series.push({
        timestamp: row.timestamp.toISOString(),
        pnl_delta: row.pnl_delta,
        equity,
      });
    }

    return series;
  } catch (err) {
    console.error('Error querying wallet data:', err);
    return [];
  }
}

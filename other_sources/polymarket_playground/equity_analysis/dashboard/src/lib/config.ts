import path from 'path';

export const DB_PATH = process.env.DUCKDB_PATH || path.resolve(process.cwd(), '../../data/polymarket.db');
export const SCORES_CSV_PATH = process.env.SCORES_CSV || path.resolve(process.cwd(), '../output/equity_scores.csv');

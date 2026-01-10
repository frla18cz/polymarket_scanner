export interface EquityScore {
  wallet: string;
  score: number;
  smoothness: number;
  sharpe: number;
  max_drawdown: number;
  net_change: number;
  equity_end: number;
  points: number;
  markets?: number;
  active_days?: number;
}

export interface WalletTimeSeriesPoint {
  timestamp: string;
  pnl_delta: number;
  equity: number;
}

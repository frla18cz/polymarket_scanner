import duckdb from 'duckdb';
import { DB_PATH } from './config';

export const query = async <T = Record<string, unknown>>(sql: string, params: unknown[] = []): Promise<T[]> => {
  return new Promise((resolve, reject) => {
    const db = new duckdb.Database(DB_PATH, duckdb.OPEN_READONLY, (err) => {
      if (err) {
        reject(err);
      } else {
        db.all(sql, params, (err2: Error | null, rows: unknown[]) => {
          db.close();
          if (err2) reject(err2);
          else resolve(rows as T[]);
        });
      }
    });
  });
};

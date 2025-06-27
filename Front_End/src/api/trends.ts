import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockSpendingTrends } from './mock/trends.mock';

export async function getSpendingTrends() {
  if (USE_SPECIFIC_REAL.trends || !USE_MOCK) {
    const res = await api.get('/trends');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockSpendingTrends;
  }
}

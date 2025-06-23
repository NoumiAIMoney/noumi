import { api } from './index';
import { USE_MOCK } from './config';
import { mockSpendingTrends } from './mock/trends.mock';

export async function getSpendingTrends() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockSpendingTrends;
  }

  const res = await api.get('/trends');
  return res.data;
}

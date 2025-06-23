import { api } from './index';
import { USE_MOCK } from './config';
import { mockWeeklySavings } from './mock/savings.mock';

export async function getWeeklySavings() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockWeeklySavings;
  }

  const res = await api.get('/savings/weekly');
  return res.data;
}

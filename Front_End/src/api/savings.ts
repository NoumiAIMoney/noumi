import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockWeeklySavings } from './mock/savings.mock';

export async function getWeeklySavings() {
  if (USE_SPECIFIC_REAL.savings || !USE_MOCK) {
    const res = await api.get('/savings/weekly');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockWeeklySavings;
  }
}

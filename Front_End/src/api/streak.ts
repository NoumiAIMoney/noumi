import { api } from './index';
import { USE_MOCK } from './config';
import { mockWeeklyStreak, mockLongestStreak } from './mock/streak.mock';

export async function getWeeklyStreak() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockWeeklyStreak;
  }

  const res = await api.get('/streak/weekly');
  return res.data;
}

export async function getLongestStreak() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockLongestStreak;
  }

  const res = await api.get('/streak/longest');
  return res.data;
}

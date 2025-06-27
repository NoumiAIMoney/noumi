import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockLongestStreak, mockWeeklyStreak } from './mock/streak.mock';

export async function getWeeklyStreak() {
  if (USE_SPECIFIC_REAL.weekly_streak || !USE_MOCK) {
    const res = await api.get('/streak/weekly');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockWeeklyStreak;
  }
}

export async function getLongestStreak() {
  if (USE_SPECIFIC_REAL.longest_streak || !USE_MOCK) {
    const res = await api.get('/streak/longest');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockLongestStreak;
  }
}

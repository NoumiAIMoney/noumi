import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockAccomplishedHabits, mockHabits } from './mock/habits.mock';

export async function getHabits() {
  if (USE_SPECIFIC_REAL.habits || !USE_MOCK) {
    const res = await api.get('/habits');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise(res => setTimeout(res, 300));
    return mockHabits;
  }
}

export async function getAccomplishedHabits() {
  if (USE_MOCK) {
    await new Promise(res => setTimeout(res, 300));
    return mockAccomplishedHabits;
  }

  const res = await api.get('/accomplished_habits');
  return res.data;
}
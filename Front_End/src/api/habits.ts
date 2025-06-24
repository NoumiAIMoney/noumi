import { api } from './index';
import { USE_MOCK } from './config';
import { mockHabits, mockAccomplishedHabits } from './mock/habits.mock';

export async function getHabits() {
  if (USE_MOCK) {
    await new Promise(res => setTimeout(res, 300));
    return mockHabits;
  }

  const res = await api.get('/habits');
  return res.data;
}

export async function getAccomplishedHabits() {
  if (USE_MOCK) {
    await new Promise(res => setTimeout(res, 300));
    return mockAccomplishedHabits;
  }

  const res = await api.get('/accomplished_habits');
  return res.data;
}
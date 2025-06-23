import { api } from './index';
import { USE_MOCK } from './config';
import { mockHabits } from './mock/habits.mock';

export async function getHabits() {
  if (USE_MOCK) {
    await new Promise(res => setTimeout(res, 300));
    return mockHabits;
  }

  const res = await api.get('/habits');
  return res.data;
}

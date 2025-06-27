import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockComputedGoal } from './mock/goal.mock';

export async function getComputedGoal() {
  if (USE_SPECIFIC_REAL.goal || !USE_MOCK) {
    const res = await api.get('/goal/computed');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise(res => setTimeout(res, 300));
    return mockComputedGoal;
  }
}

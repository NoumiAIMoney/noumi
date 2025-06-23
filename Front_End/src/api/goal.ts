import { api } from './index';
import { USE_MOCK } from './config';
import { mockComputedGoal } from './mock/goal.mock';

export async function getComputedGoal() {
  if (USE_MOCK) {
    await new Promise(res => setTimeout(res, 300));
    return mockComputedGoal;
  }

  const res = await api.get('/goal/computed');
  return res.data;
}

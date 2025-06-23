import { api } from './index';
import { USE_MOCK } from './config';
import { mockPlaidResponse } from './mock/plaid.mock';

export async function connectPlaid(public_token: string) {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockPlaidResponse;
  }

  const res = await api.post('/plaid/connect', { public_token });
  return res.data;
}

import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockPlaidResponse } from './mock/plaid.mock';

export async function connectPlaid(public_token: string) {
  if(USE_SPECIFIC_REAL.plaid || !USE_MOCK) {
    const res = await api.post('/plaid/connect', { public_token });
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockPlaidResponse;
  }
}

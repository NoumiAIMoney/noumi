import { api } from './index';
import { USE_MOCK } from './config';
import { mockYearlyAnomalies } from './mock/anomalies.mock';

export async function getYearlyAnomalies() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockYearlyAnomalies;
  }

  const res = await api.get('/anomalies/yearly');
  return res.data;
}

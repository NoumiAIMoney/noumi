import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockYearlyAnomalies } from './mock/anomalies.mock';

export async function getYearlyAnomalies() {
  if (USE_SPECIFIC_REAL.anomalies || !USE_MOCK) {
    const res = await api.get('/anomalies/yearly');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockYearlyAnomalies;
  }
}

import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import {
  mockSpendingCategories,
  mockSpendingStatus,
  mockTotalSpending,
} from './mock/spending.mock';

export async function getSpendingCategories() {
  if (USE_SPECIFIC_REAL.spending_categories || !USE_MOCK) {
    const res = await api.get('/spending/categories');
    return res.data;
  }
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockSpendingCategories;
  }
}

export async function getSpendingStatus() {
  if (USE_SPECIFIC_REAL.spending_status || !USE_MOCK) {
    const res = await api.get('/spending/status');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockSpendingStatus;
  }
}

export async function getTotalSpending() {
  if (USE_SPECIFIC_REAL.spending_total || !USE_MOCK) {
    const res = await api.get('/spending/total');
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockTotalSpending;
  }
}

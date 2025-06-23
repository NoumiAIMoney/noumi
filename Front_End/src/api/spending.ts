import { api } from './index';
import { USE_MOCK } from './config';
import {
  mockSpendingCategories,
  mockSpendingStatus,
  mockTotalSpending,
} from './mock/spending.mock';

export async function getSpendingCategories() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockSpendingCategories;
  }
  const res = await api.get('/spending/categories');
  return res.data;
}

export async function getSpendingStatus() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockSpendingStatus;
  }
  const res = await api.get('/spending/status');
  return res.data;
}

export async function getTotalSpending() {
  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockTotalSpending;
  }
  const res = await api.get('/spending/total');
  return res.data;
}

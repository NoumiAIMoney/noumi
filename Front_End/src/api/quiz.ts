import { USE_MOCK, USE_SPECIFIC_REAL } from './config';
import { api } from './index';
import { mockQuizResponse } from './mock/quiz.mock';

export async function submitQuiz(data: {
  goal_name: string;
  goal_description: string;
  goal_amount: number;
  target_date: string;
  net_monthly_income: number;
}) {
  if (USE_SPECIFIC_REAL.quiz || !USE_MOCK) {
    const res = await api.post('/quiz', data);
    return res.data;
  }

  if (USE_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return mockQuizResponse;
  }
}

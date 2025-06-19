import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Change this to your FastAPI server URL

interface SignUpData {
  email: string;
  password: string;
  name: string;
}

interface QuizData {
  user_id: string;
  answers: {
    [key: string]: any;
  };
}

export const api = {
  async signUp(data: SignUpData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/signup`, data);
      return response.data;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  },

  async submitQuiz(data: QuizData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/quiz`, data);
      return response.data;
    } catch (error) {
      console.error('Quiz submission error:', error);
      throw error;
    }
  }
};

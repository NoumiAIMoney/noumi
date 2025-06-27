import axios from 'axios';

const MOCK_TOKEN = "mock_jwt_token";

export const api = axios.create({
  baseURL: 'https://1c17-2603-7000-88f0-99f0-182a-f89a-fba4-76d.ngrok-free.app',
  timeout: 10000000,
});

api.defaults.headers.common['Authorization'] = `Bearer ${MOCK_TOKEN}`;

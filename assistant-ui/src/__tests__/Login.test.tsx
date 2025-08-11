import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock config to avoid import.meta issues
jest.mock('../config', () => ({
  API_BASE_URL: 'http://localhost:8000',
  SOME_PUBLIC_CONFIG: 'test-value'
}));

// Mock API
jest.mock('../api/request', () => ({
  default: {
    post: jest.fn()
  }
}));

// Mock auth utils
jest.mock('../utils/auth', () => ({
  setAuthData: jest.fn(),
  isAuthenticated: jest.fn(() => false)
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ state: null }),
}));

import Login from '../pages/Login';

describe('Login', () => {
  it('用户可以输入账号密码并点击登录', () => {
    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText('请输入用户名'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByPlaceholderText('请输入密码'), { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: '登录' }));
    // 断言登录表单存在
    expect(screen.getByPlaceholderText('请输入用户名')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('请输入密码')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument();
  });
});

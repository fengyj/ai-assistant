import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock config to avoid import.meta issues
jest.mock('../config', () => ({
  API_BASE_URL: 'http://localhost:8000',
  SOME_PUBLIC_CONFIG: 'test-value'
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

// Mock API
jest.mock('../api/request', () => ({
  default: {
    post: jest.fn()
  }
}));

// Mock auth utils
jest.mock('../utils/auth', () => ({
  setToken: jest.fn(),
  isAuthenticated: jest.fn(() => false)
}));

import Login from '../pages/Login';

describe('Login', () => {
  it('用户可以输入账号密码并点击登录', () => {
    render(<Login />);
    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));
    // 断言登录表单存在
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
  });
});

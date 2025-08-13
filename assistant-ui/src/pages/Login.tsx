import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { ArrowPathIcon } from "@heroicons/react/24/outline";
import { isAuthenticated } from "../utils/auth";
import { useUserSession } from "../hooks/useUserSession";
import { login, type LoginRequest } from "../api/auth";

const Login: React.FC = () => {
  const { setUser } = useUserSession();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get the path the user was trying to access before being redirected to login
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/";

  // 如果已经登录，直接跳转到主页
  useEffect(() => {
    if (isAuthenticated()) {
      navigate(from, { replace: true });
    }
  }, [navigate, from]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      setError("请输入用户名和密码");
      return;
    }
    
    setError("");
    setIsLoading(true);
    console.log("Attempting login with:", username);
    
    try {
      const credentials: LoginRequest = {
        username: username.trim(),
        password
      };
      
      const response = await login(credentials);
      console.log("Login response:", response);
      
      // 登录成功，用户信息已通过 setAuthData 存储并触发 authChanged 事件
      // UserSessionContext 会自动更新用户状态
      setUser(response.user);
      console.log("Auth data set, navigating to:", from);
      
      // 登录成功后跳转到目标页面
      navigate(from, { replace: true });
      
    } catch (error: unknown) {
      console.error("Login error:", error);
      
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status: number; data?: { message?: string } } };
        if (axiosError.response?.status === 401) {
          setError("用户名或密码错误");
        } else if (axiosError.response?.status === 403) {
          setError("账户已被禁用，请联系管理员");
        } else if (axiosError.response?.status && axiosError.response.status >= 500) {
          setError("服务器错误，请稍后重试");
        } else {
          setError(axiosError.response?.data?.message || "登录失败，请重试");
        }
      } else if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("登录过程中发生未知错误");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="centered-page bg-gray-50 dark:bg-gray-900">
      <form onSubmit={handleSubmit} className="auth-login-card p-8 w-96">
        <h2 className="mb-6 text-2xl font-bold text-center text-gray-800 dark:text-gray-100">登录</h2>
        
        <div className="mb-4">
          <label htmlFor="username" className="login-label">
            用户名
          </label>
          <input
            id="username"
            className="login-input"
            type="text"
            placeholder="请输入用户名"
            value={username}
            onChange={e => setUsername(e.target.value)}
            disabled={isLoading}
            required
          />
        </div>
        
        <div className="mb-6">
          <label htmlFor="password" className="login-label">
            密码
          </label>
          <input
            id="password"
            className="login-input"
            type="password"
            placeholder="请输入密码"
            value={password}
            onChange={e => setPassword(e.target.value)}
            disabled={isLoading}
            required
          />
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-md text-sm">
            {error}
          </div>
        )}
        
        <button 
          className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 dark:disabled:bg-blue-700 text-white p-3 rounded-md font-medium transition-colors duration-200 centered-container" 
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <ArrowPathIcon className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
              登录中...
            </>
          ) : (
            "登录"
          )}
        </button>
      </form>
    </div>
  );
};

export default Login;

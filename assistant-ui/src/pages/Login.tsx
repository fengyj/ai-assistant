import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { setToken, isAuthenticated } from "../utils/auth";
import api from "../api/request";

const Login: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // 如果已经登录，直接跳转到主页
  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/", { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    console.log("Attempting login with:", username);
    
    try {
      const res = await api.post("/api/users/login", { username, password });
      console.log("Login response:", res.data);
      
      if (res.data.access_token) {
        setToken(res.data.access_token);
        console.log("Token set, navigating to home...");
        // 登录成功后立即跳转
        navigate("/", { replace: true });
      } else {
        console.error("No access token in response");
        setError("Login failed - no token received");
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Invalid username or password");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow w-80">
        <h2 className="mb-4 text-xl font-bold">Login</h2>
        <input
          className="mb-2 w-full p-2 border rounded"
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          className="mb-2 w-full p-2 border rounded"
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button className="w-full bg-blue-500 text-white p-2 rounded" type="submit">Login</button>
        {error && <div className="mt-2 text-red-500">{error}</div>}
      </form>
    </div>
  );
};

export default Login;

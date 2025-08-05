// Mock for Vite environment variables
export const mockEnv = {
  VITE_API_BASE_URL: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
  VITE_SOME_PUBLIC_CONFIG: process.env.VITE_SOME_PUBLIC_CONFIG || 'test-value',
  // 添加其他环境变量...
};

// Setup import.meta.env mock
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: mockEnv
    }
  }
});

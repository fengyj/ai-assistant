import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Polyfill for TextEncoder/TextDecoder in Jest environment
Object.assign(global, { TextEncoder, TextDecoder });

// Import Vite environment mock
import './__mocks__/vite-env';
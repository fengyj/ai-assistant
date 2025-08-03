import { getMockAIResponse } from '../utils/mockAI';

describe('getMockAIResponse', () => {
  it('returns mock AI response', () => {
    const result = getMockAIResponse('hello');
    expect(result).toContain('hello');
  });
});

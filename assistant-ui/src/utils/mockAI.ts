// mockAI.ts
// Mock AI response logic for ConversationContext
// Extracted for separation of concerns

export function getMockAIResponse(content: string): string {
  return `这是对"${content}"的回复。这是一个模拟的AI响应，用于测试界面功能。在实际应用中，这里应该调用AI API来获取真实的回复。`;
}

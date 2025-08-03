// useEditingMessage.ts
// Custom hook for editing message state logic
import { useState } from 'react';

export function useEditingMessage<T extends { id: string; content: string }>() {
  const [editingMessage, setEditingMessage] = useState<T | null>(null);
  return { editingMessage, setEditingMessage };
}

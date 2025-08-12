import { useContext } from 'react';
import { ModelContext } from '../context/ModelContext';
import type { ModelContextData } from '../context/ModelContext';

// Hook for consuming the model context
export const useModel = (): ModelContextData => {
  const context = useContext(ModelContext);
  if (context === undefined) {
    throw new Error('useModel must be used within a ModelProvider');
  }
  return context;
};

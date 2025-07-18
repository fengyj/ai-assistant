// CSS class utilities for consistent styling across components

export const themeClasses = {
  bg: {
    primary: 'bg-white dark:bg-gray-800',
    secondary: 'bg-gray-50 dark:bg-gray-700',
    sidebar: 'bg-white dark:bg-gray-800',
    input: 'bg-transparent',
    button: 'bg-gray-100 dark:bg-gray-700'
  },
  text: {
    primary: 'text-gray-900 dark:text-white',
    secondary: 'text-gray-600 dark:text-gray-300',
    muted: 'text-gray-500 dark:text-gray-400',
    accent: 'text-blue-600 dark:text-blue-400'
  },
  border: {
    primary: 'border-gray-200 dark:border-gray-700',
    secondary: 'border-gray-300 dark:border-gray-600',
    focus: 'border-blue-500 dark:border-blue-400'
  },
  hover: {
    bg: 'hover:bg-gray-50 dark:hover:bg-gray-700',
    text: 'hover:text-gray-700 dark:hover:text-gray-200'
  }
};

export const getButtonClasses = (variant: 'primary' | 'secondary' | 'danger' = 'secondary', isDarkMode = false) => {
  const base = 'px-4 py-2 rounded-md transition-colors font-medium';
  
  switch (variant) {
    case 'primary':
      return `${base} bg-blue-600 text-white hover:bg-blue-700`;
    case 'danger':
      return `${base} text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20`;
    default:
      return `${base} ${isDarkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'}`;
  }
};

export const getInputClasses = (isDarkMode = false) => {
  return `w-full px-3 py-2 border rounded-md ${
    isDarkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
  } focus:ring-2 focus:ring-blue-500 focus:border-transparent`;
};

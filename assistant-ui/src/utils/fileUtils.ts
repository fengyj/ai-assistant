// 文件处理工具函数

/**
 * 从粘贴事件中提取文件
 */
export const extractFilesFromPaste = (event: ClipboardEvent): File[] => {
  const files: File[] = [];
  
  if (event.clipboardData?.files) {
    Array.from(event.clipboardData.files).forEach(file => {
      files.push(file);
    });
  }
  
  return files;
};

/**
 * 验证文件类型
 */
export const isValidFileType = (file: File, acceptedTypes: string[]): boolean => {
  if (acceptedTypes.length === 0) return true;
  
  return acceptedTypes.some(type => {
    if (type.endsWith('/*')) {
      return file.type.startsWith(type.slice(0, -1));
    }
    return file.type === type;
  });
};

/**
 * 格式化文件大小
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * 获取文件扩展名
 */
export const getFileExtension = (filename: string): string => {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2);
};

/**
 * 判断是否为图片文件
 */
export const isImageFile = (file: File): boolean => {
  return file.type.startsWith('image/');
};

/**
 * 判断是否为文档文件
 */
export const isDocumentFile = (file: File): boolean => {
  const documentTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/csv',
  ];
  
  return documentTypes.includes(file.type) || file.type.startsWith('text/');
};

/**
 * 生成文件预览URL（仅用于图片）
 */
export const generateFilePreviewUrl = (file: File): string | null => {
  if (!isImageFile(file)) return null;
  return URL.createObjectURL(file);
};

/**
 * 清理文件预览URL
 */
export const revokeFilePreviewUrl = (url: string): void => {
  URL.revokeObjectURL(url);
};

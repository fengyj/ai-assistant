import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  PaperClipIcon,
  XMarkIcon,
  DocumentIcon,
  PhotoIcon,
  FilmIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

interface FileUploadProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number; // 字节
  acceptedFileTypes?: string[];
  className?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  files,
  onFilesChange,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedFileTypes = [
    'image/*',
    'text/*',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  ],
  className = '',
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // 获取文件图标
  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) {
      return <PhotoIcon className="w-4 h-4" />;
    }
    if (fileType.startsWith('video/')) {
      return <FilmIcon className="w-4 h-4" />;
    }
    if (fileType.includes('pdf') || fileType.includes('document') || fileType.includes('word')) {
      return <DocumentTextIcon className="w-4 h-4" />;
    }
    return <DocumentIcon className="w-4 h-4" />;
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 验证文件
  const validateFile = useCallback((file: File): string | null => {
    if (file.size > maxSize) {
      return `文件 "${file.name}" 过大，最大支持 ${formatFileSize(maxSize)}`;
    }
    
    if (acceptedFileTypes.length > 0) {
      const isAccepted = acceptedFileTypes.some(type => {
        if (type.endsWith('/*')) {
          return file.type.startsWith(type.slice(0, -1));
        }
        return file.type === type;
      });
      
      if (!isAccepted) {
        return `文件 "${file.name}" 格式不支持`;
      }
    }
    
    return null;
  }, [maxSize, acceptedFileTypes]);

  // 处理文件添加
  const handleFilesAdd = useCallback((newFiles: File[]) => {
    setUploadError(null);
    
    // 验证文件数量
    if (files.length + newFiles.length > maxFiles) {
      setUploadError(`最多只能上传 ${maxFiles} 个文件`);
      return;
    }

    // 验证每个文件
    const validFiles: File[] = [];
    for (const file of newFiles) {
      const error = validateFile(file);
      if (error) {
        setUploadError(error);
        return;
      }
      
      // 检查是否已存在同名文件
      if (files.some(f => f.name === file.name && f.size === file.size)) {
        continue; // 跳过重复文件
      }
      
      validFiles.push(file);
    }

    if (validFiles.length > 0) {
      onFilesChange([...files, ...validFiles]);
    }
  }, [files, maxFiles, onFilesChange, validateFile]);

  // 处理文件删除
  const handleFileRemove = useCallback((index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    onFilesChange(newFiles);
    setUploadError(null);
  }, [files, onFilesChange]);

  // 拖拽配置
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleFilesAdd,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    onDropAccepted: () => setDragActive(false),
    onDropRejected: () => setDragActive(false),
    maxFiles: maxFiles - files.length,
    maxSize,
    accept: acceptedFileTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {} as Record<string, string[]>),
    noClick: false,
    noKeyboard: false,
  });

  return (
    <div className={`chat-file-upload-container ${className}`}>
      <div className="chat-file-upload-inline">
        {/* 文件上传按钮 */}
        <div
          {...getRootProps()}
          className={`chat-file-upload-dropzone ${
            isDragActive || dragActive ? 'drag-active' : ''
          }`}
        >
          <input {...getInputProps()} />
          <button
            type="button"
            className="chat-file-upload-button"
            title="上传文件"
          >
            <PaperClipIcon className="w-4 h-4" />
            {files.length > 0 && (
              <span className="chat-file-count-badge">{files.length}</span>
            )}
          </button>
        </div>

        {/* 已上传文件列表 - 水平排列 */}
        {files.length > 0 && (
          <div className="chat-file-list-inline">
            {files.map((file, index) => (
              <div key={`${file.name}-${index}`} className="chat-file-item-inline">
                <div className="chat-file-item-icon">
                  {getFileIcon(file.type)}
                </div>
                <div className="chat-file-item-info">
                  <span className="chat-file-item-name" title={file.name}>
                    {file.name.length > 15 
                      ? `${file.name.slice(0, 12)}...` 
                      : file.name
                    }
                  </span>
                  <span className="chat-file-item-size">
                    {formatFileSize(file.size)}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => handleFileRemove(index)}
                  className="chat-file-item-remove"
                  title="删除文件"
                >
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 拖拽覆盖层 */}
      {(isDragActive || dragActive) && (
        <div className="chat-file-upload-overlay">
          <div className="chat-file-upload-overlay-content">
            <PaperClipIcon className="w-8 h-8 text-blue-500" />
            <p className="text-sm font-medium text-blue-600 dark:text-blue-400">
              拖拽文件到这里上传
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              支持最多 {maxFiles} 个文件，单个文件最大 {formatFileSize(maxSize)}
            </p>
          </div>
        </div>
      )}

      {/* 错误提示 */}
      {uploadError && (
        <div className="chat-file-upload-error">
          <span className="text-xs text-red-600 dark:text-red-400">
            {uploadError}
          </span>
        </div>
      )}
    </div>
  );
};

import * as React from 'react';
import { ChangeEvent, useRef } from 'react';

interface FileInputProps {
  id: string;
  label?: string;
  accept?: string;
  onChange: (file: File | null) => void;
  disabled?: boolean;
  buttonText?: string;
  className?: string;
  required?: boolean;
}

const FileInput: React.FC<FileInputProps> = ({
  id,
  label,
  accept = '*',
  onChange,
  disabled = false,
  buttonText = 'Select File',
  className = '',
  required = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    onChange(file);
  };

  return (
    <div className={className}>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="flex items-center">
        <input
          ref={fileInputRef}
          id={id}
          type="file"
          accept={accept}
          onChange={handleChange}
          disabled={disabled}
          required={required}
          className="file:mr-4 file:py-2 file:px-4
                   file:rounded-md file:border-0
                   file:text-sm file:font-semibold
                   file:bg-indigo-50 file:text-indigo-700
                   hover:file:bg-indigo-100
                   text-sm text-gray-500
                   focus:outline-none"
        />
      </div>
    </div>
  );
};

export default FileInput;
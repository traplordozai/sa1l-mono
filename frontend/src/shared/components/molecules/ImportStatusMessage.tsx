import * as React from 'react';

interface ImportStatusMessageProps {
  message: string;
  errors?: string[];
  className?: string;
}

const ImportStatusMessage: React.FC<ImportStatusMessageProps> = ({
  message,
  errors = [],
  className = '',
}) => {
  if (!message) return null;

  const isError = message.includes('Error') || message.includes('Failed') || message.includes('failed');
  const isWarning = errors.length > 0 && !isError;

  let bgColorClass = 'bg-green-50 text-green-700';
  if (isError) {
    bgColorClass = 'bg-red-50 text-red-700';
  } else if (isWarning) {
    bgColorClass = 'bg-yellow-50 text-yellow-700';
  }

  return (
    <div className={`p-3 rounded-md ${bgColorClass} ${className}`}>
      <p>{message}</p>

      {errors.length > 0 && (
        <div className="mt-2">
          <h4 className="text-sm font-medium mb-1">
            {isError ? 'Errors:' : 'Warnings:'}
          </h4>
          <ul className="list-disc list-inside text-xs">
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ImportStatusMessage;
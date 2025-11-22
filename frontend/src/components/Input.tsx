import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-2xl font-bold text-gray-900 mb-4">
          {label}
        </label>
      )}
      <input
        className={`w-full px-8 py-6 text-2xl border-4 rounded-xl focus:outline-none transition-colors ${
          error 
            ? 'border-red-500 focus:border-red-600' 
            : 'border-gray-300 focus:border-blue-500'
        } ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-2 text-lg text-red-600 font-semibold">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-2 text-lg text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg' | 'xl';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'lg',
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'font-bold rounded-2xl transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100';
  
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-xl',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300 active:bg-gray-400',
    ghost: 'bg-white text-gray-700 border-4 border-gray-200 hover:border-blue-300',
    danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 shadow-xl'
  };
  
  const sizeStyles = {
    sm: 'px-6 py-3 text-lg',
    md: 'px-8 py-4 text-xl',
    lg: 'px-12 py-6 text-2xl',
    xl: 'px-20 py-10 text-4xl shadow-2xl'
  };
  
  const widthStyle = fullWidth ? 'w-full' : '';
  
  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyle} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

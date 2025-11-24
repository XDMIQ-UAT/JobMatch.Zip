import React from 'react';

type CardVariant = 'default' | 'info' | 'success' | 'warning' | 'error';

interface CardProps {
  variant?: CardVariant;
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  children,
  className = ''
}) => {
  const baseStyles = 'rounded-3xl p-8 md:p-12';
  
  const variantStyles = {
    default: 'bg-white shadow-lg',
    info: 'bg-blue-50 border-4 border-blue-200',
    success: 'bg-green-50 border-4 border-green-300',
    warning: 'bg-yellow-50 border-4 border-yellow-200',
    error: 'bg-red-50 border-4 border-red-200'
  };
  
  return (
    <div className={`${baseStyles} ${variantStyles[variant]} ${className}`}>
      {children}
    </div>
  );
};

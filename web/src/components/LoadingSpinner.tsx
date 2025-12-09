interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export default function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  };
  
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className={`${sizeClasses[size]} relative`}>
        {/* 외부 원 */}
        <div className="absolute inset-0 rounded-full border-2 border-dark-700" />
        
        {/* 회전하는 원 */}
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-primary-500 animate-spin" />
        
        {/* 내부 점 */}
        <div className="absolute inset-2 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 animate-pulse-slow" />
      </div>
      
      {text && (
        <p className="text-sm text-dark-400 animate-pulse">{text}</p>
      )}
    </div>
  );
}


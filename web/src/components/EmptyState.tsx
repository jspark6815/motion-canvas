interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export default function EmptyState({ 
  title, 
  description, 
  icon,
  action 
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
      {/* 아이콘 */}
      <div className="w-20 h-20 rounded-full bg-dark-800 flex items-center justify-center mb-6">
        {icon || (
          <svg 
            className="w-10 h-10 text-dark-500" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={1.5} 
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" 
            />
          </svg>
        )}
      </div>
      
      {/* 텍스트 */}
      <h3 className="text-xl font-semibold text-dark-200 mb-2">
        {title}
      </h3>
      
      {description && (
        <p className="text-dark-400 max-w-md mb-6">
          {description}
        </p>
      )}
      
      {/* 액션 버튼 */}
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white font-medium transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}


import React from 'react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-12" role="status" aria-live="polite">
      <div className="relative w-20 h-20">
        {/* Outer ring */}
        <div className="absolute top-0 left-0 w-full h-full border-4 border-carbon-gray-20 rounded-full"></div>
        {/* Spinning ring */}
        <div className="absolute top-0 left-0 w-full h-full border-4 border-carbon-blue-60 rounded-full border-t-transparent border-r-transparent animate-spin"></div>
      </div>
      <p className="mt-6 text-carbon-gray-100 font-semibold text-base tracking-wide">
        Analisando transcrição...
      </p>
      <p className="mt-2 text-sm text-carbon-gray-70">
        Isso pode levar de 10 a 30 segundos
      </p>
      <div className="mt-4 flex gap-1">
        <div className="w-2 h-2 bg-carbon-blue-60 rounded-full animate-pulse"></div>
        <div className="w-2 h-2 bg-carbon-blue-60 rounded-full animate-pulse delay-75"></div>
        <div className="w-2 h-2 bg-carbon-blue-60 rounded-full animate-pulse delay-150"></div>
      </div>
    </div>
  );
};

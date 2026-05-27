import React from 'react';

interface TextAreaInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const TextAreaInput: React.FC<TextAreaInputProps> = ({
  value,
  onChange,
  placeholder = 'Cole aqui a transcrição da entrevista (mínimo 50 palavras, recomendado 150+ para melhor resultado)...',
  disabled = false,
}) => {
  const wordCount = value.trim().split(/\s+/).filter(word => word.length > 0).length;

  return (
    <div className="w-full">
      <div className="mb-3 flex justify-between items-center">
        <label 
          htmlFor="transcript-input" 
          className="block text-sm font-semibold text-carbon-gray-100 tracking-wide"
        >
          Transcrição da entrevista
        </label>
        <span className="text-sm text-carbon-gray-70 font-ibm-plex-mono">
          {wordCount} {wordCount === 1 ? 'palavra' : 'palavras'}
        </span>
      </div>
      <textarea
        id="transcript-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full h-64 px-4 py-3 bg-carbon-gray-10 border-b-2 border-carbon-gray-80 text-carbon-gray-100 placeholder:text-carbon-gray-50 focus:bg-white focus:border-carbon-blue-60 focus:outline-none resize-none disabled:bg-carbon-gray-20 disabled:cursor-not-allowed disabled:text-carbon-gray-50 transition-colors font-ibm-plex-sans text-sm leading-relaxed"
        aria-label="Entrada da transcrição"
      />
      <div className="mt-2 text-xs text-carbon-gray-60">
        {wordCount < 50 && wordCount > 0 && (
          <span className="text-carbon-red-60">
            ⚠ Use pelo menos 50 palavras para a análise
          </span>
        )}
        {wordCount >= 50 && wordCount < 150 && (
          <span className="text-carbon-yellow-60">
            ℹ Recomendado 150+ palavras para melhor confiabilidade
          </span>
        )}
        {wordCount >= 150 && (
          <span className="text-carbon-green-60">
            ✓ Quantidade de palavras adequada para análise
          </span>
        )}
      </div>
    </div>
  );
};

import { useState, useCallback } from 'react';
import type { DISCAnalysisResult } from '../constants/discFramework';

export type AnalysisMode = 'demo' | 'openrouter' | 'anthropic' | 'gemini' | 'openai';

interface UseDISCAnalysisReturn {
  analyze: (transcript: string, mode: AnalysisMode) => Promise<DISCAnalysisResult>;
  loading: boolean;
  error: string | null;
  result: DISCAnalysisResult | null;
  clearError: () => void;
  clearResult: () => void;
}

const buildDemoAnalysis = (transcript: string): DISCAnalysisResult => {
  const text = transcript.toLowerCase();

  let D = 35;
  let I = 35;
  let S = 35;
  let C = 35;

  const dominanceKeywords = ['resultado', 'decidir', 'meta', 'prazo', 'rápido', 'executar', 'foco'];
  const influenceKeywords = ['equipe', 'pessoas', 'engajar', 'motivar', 'energia', 'comunicação', 'entusiasmo'];
  const steadinessKeywords = ['estável', 'apoio', 'calma', 'harmonia', 'consenso', 'colaboração', 'constante'];
  const conscientiousKeywords = ['dados', 'processo', 'qualidade', 'análise', 'detalhe', 'precisão', 'risco'];

  const countKeywords = (keywords: string[]) => {
    return keywords.reduce((acc, keyword) => {
      return acc + (text.includes(keyword) ? 1 : 0);
    }, 0);
  };

  D += countKeywords(dominanceKeywords) * 8;
  I += countKeywords(influenceKeywords) * 8;
  S += countKeywords(steadinessKeywords) * 8;
  C += countKeywords(conscientiousKeywords) * 8;

  const scores = {
    D: Math.min(95, D),
    I: Math.min(95, I),
    S: Math.min(95, S),
    C: Math.min(95, C),
  };

  const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  const primary = sorted[0][0] as 'D' | 'I' | 'S' | 'C';
  const secondary = sorted[1][0] as 'D' | 'I' | 'S' | 'C';

  const summaryByPrimary: Record<'D' | 'I' | 'S' | 'C', string> = {
    D: 'Perfil com maior tendência a Dominância, com foco em decisão e execução. A comunicação indica orientação a resultados e senso de urgência.',
    I: 'Perfil com maior tendência a Influência, com forte viés de relacionamento e energia social. A comunicação mostra engajamento, persuasão e otimismo.',
    S: 'Perfil com maior tendência a Estabilidade, valorizando cooperação e ritmo consistente. A comunicação sugere apoio ao time e busca de harmonia.',
    C: 'Perfil com maior tendência a Conformidade, com atenção a qualidade e método. A comunicação demonstra análise, precisão e cautela em decisões.',
  };

  return {
    overall_profile: {
      primary,
      secondary,
      scores,
      summary: `${summaryByPrimary[primary]} Resultado gerado em modo Demo para validação visual do relatório.`,
    },
    detailed_breakdown: [
      {
        trait: 'Dominância',
        score: scores.D,
        evidence: [
          'Sinal de foco em objetivos e velocidade de execução detectado no texto.',
          'Presença de linguagem orientada a decisão e resultado (modo Demo).',
        ],
        analysis: 'Indicadores de assertividade e orientação a performance.',
      },
      {
        trait: 'Influência',
        score: scores.I,
        evidence: [
          'Referências a comunicação e engajamento interpessoal identificadas.',
          'Sinal de linguagem colaborativa e motivacional (modo Demo).',
        ],
        analysis: 'Indicadores de sociabilidade, entusiasmo e capacidade de influência.',
      },
      {
        trait: 'Estabilidade',
        score: scores.S,
        evidence: [
          'Termos ligados a estabilidade e suporte ao grupo foram observados.',
          'Sinal de busca por previsibilidade e cooperação (modo Demo).',
        ],
        analysis: 'Indicadores de consistência, paciência e foco em relações estáveis.',
      },
      {
        trait: 'Conformidade',
        score: scores.C,
        evidence: [
          'Elementos de método, qualidade e análise foram identificados.',
          'Sinal de preocupação com critérios e precisão (modo Demo).',
        ],
        analysis: 'Indicadores de rigor, estrutura e tomada de decisão baseada em critérios.',
      },
    ],
    recommendations: [
      'Use o modo OpenAI para obter evidências textuais reais e maior precisão.',
      'Forneça transcrições com 150+ palavras para melhorar confiabilidade.',
      'Compare resultados entre entrevistas diferentes para reduzir viés situacional.',
    ],
    confidence: 'medium',
  };
};

export const useDISCAnalysis = (): UseDISCAnalysisReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DISCAnalysisResult | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
  }, []);

  const analyze = useCallback(async (transcript: string, mode: AnalysisMode): Promise<DISCAnalysisResult> => {
    // Validation
    if (!transcript || transcript.trim().length === 0) {
      const errorMsg = 'Insira uma transcrição para analisar.';
      setError(errorMsg);
      throw new Error(errorMsg);
    }

    const wordCount = transcript.trim().split(/\s+/).length;
    if (wordCount < 50) {
      const errorMsg = `A transcrição está muito curta (${wordCount} palavras). Forneça pelo menos 50 palavras para uma análise significativa.`;
      setError(errorMsg);
      throw new Error(errorMsg);
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (mode === 'demo') {
        const demoResult = buildDemoAnalysis(transcript);
        setResult(demoResult);
        setLoading(false);
        return demoResult;
      }

      const response = await fetch(`${import.meta.env.BASE_URL}api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript, mode }),
      });

      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMsg = payload?.error || 'Não foi possível concluir a análise.';
        setError(errorMsg);
        setLoading(false);
        throw new Error(errorMsg);
      }

      const parsedResult = payload as DISCAnalysisResult;
      if (!parsedResult.overall_profile || !parsedResult.detailed_breakdown) {
        throw new Error('Formato de resposta inválido da API.');
      }

      setResult(parsedResult);
      setLoading(false);
      return parsedResult;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Ocorreu um erro desconhecido.';
      setError(errorMessage);
      setLoading(false);
      throw err;
    }
  }, []);

  return {
    analyze,
    loading,
    error,
    result,
    clearError,
    clearResult,
  };
};

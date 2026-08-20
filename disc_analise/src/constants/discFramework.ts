export const DISC_FRAMEWORK = `
Framework DISC para análise comportamental:
- D (Dominância): foco em resultado, decisão e assertividade.
- I (Influência): foco em comunicação, persuasão e relacionamento.
- S (Estabilidade): foco em cooperação, consistência e suporte.
- C (Conformidade): foco em método, qualidade e precisão.
`;

export type DISCDimension = 'D' | 'I' | 'S' | 'C';

export interface DISCScore {
  D: number;
  I: number;
  S: number;
  C: number;
}

export interface DetailedBreakdown {
  trait: string;
  score: number;
  evidence: string[];
  analysis: string;
}

export interface DISCAnalysisResult {
  overall_profile: {
    primary: DISCDimension;
    secondary?: DISCDimension;
    scores: DISCScore;
    summary: string;
  };
  detailed_breakdown: DetailedBreakdown[];
  recommendations: string[];
  confidence: 'high' | 'medium' | 'low';
}

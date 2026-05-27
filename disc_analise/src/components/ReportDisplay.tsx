import React from 'react';
import { Download, CheckCheck, TrendingUp } from 'lucide-react';
import type { DISCAnalysisResult } from '../constants/discFramework';

interface ReportDisplayProps {
  result: DISCAnalysisResult;
  interviewer?: string;
  interviewee?: string;
}

const clampScore = (score: number) => Math.min(Math.max(Math.round(score), 0), 100);
const logoUrl = `${import.meta.env.BASE_URL}lideranca_conectada.png`;

export const ReportDisplay: React.FC<ReportDisplayProps> = ({ result, interviewer, interviewee }) => {
  const reportRef = React.useRef<HTMLDivElement>(null);
  const [exported, setExported] = React.useState(false);
  const [exporting, setExporting] = React.useState(false);

  const scoreEntries = (Object.entries(result.overall_profile.scores) as Array<[string, number]>).map(
    ([dimension, value]) => [dimension, clampScore(value)] as [string, number],
  );
  const orderedDimensions = ['D', 'I', 'S', 'C'];
  const averageScore = Math.round(
    scoreEntries.reduce((acc, [, value]) => acc + value, 0) / Math.max(scoreEntries.length, 1),
  );
  const sortedByScore = [...scoreEntries].sort((a, b) => b[1] - a[1]);
  const highestDimension = sortedByScore[0]?.[0] || result.overall_profile.primary;
  const highestScore = sortedByScore[0]?.[1] || 0;
  const lowestDimension = sortedByScore[sortedByScore.length - 1]?.[0] || result.overall_profile.primary;
  const lowestScore = sortedByScore[sortedByScore.length - 1]?.[1] || 0;
  const scoreRange = highestScore - lowestScore;

  const getDimensionLabel = (dimension: string) => {
    switch (dimension) {
      case 'D':
        return 'Dominância';
      case 'I':
        return 'Influência';
      case 'S':
        return 'Estabilidade';
      case 'C':
        return 'Conformidade';
      default:
        return 'Indefinido';
    }
  };

  const getAreaLabel = (dimension: string) => {
    switch (dimension) {
      case 'D':
        return 'Liderança e Tomada de Decisão';
      case 'I':
        return 'Comunicação e Influência';
      case 'S':
        return 'Colaboração e Estabilidade';
      case 'C':
        return 'Organização e Qualidade';
      default:
        return 'Área comportamental';
    }
  };

  const getConfidenceLabel = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return 'Alta';
      case 'medium':
        return 'Média';
      case 'low':
        return 'Baixa';
      default:
        return confidence;
    }
  };

  const getDimensionByTrait = (trait: string): 'D' | 'I' | 'S' | 'C' | '' => {
    const normalized = trait
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');

    if (normalized.includes('domin')) return 'D';
    if (normalized.includes('influ')) return 'I';
    if (normalized.includes('stead') || normalized.includes('estab')) return 'S';
    if (normalized.includes('consc') || normalized.includes('confor')) return 'C';

    return '';
  };

  const handleExport = async () => {
    if (!reportRef.current || exporting) {
      return;
    }

    try {
      setExporting(true);

      const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
        import('html2canvas'),
        import('jspdf'),
      ]);
      await new Promise<void>((resolve) => {
        requestAnimationFrame(() => resolve());
      });

      const canvas = await html2canvas(reportRef.current, {
        scale: 3,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false,
        windowWidth: 1120,
        ignoreElements: (element) => element.getAttribute('data-pdf-ignore') === 'true',
      });

      const imageData = canvas.toDataURL('image/png', 1.0);
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
        compress: true,
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 8;
      const printableWidth = pageWidth - margin * 2;
      const printableHeight = pageHeight - margin * 2;
      const imageHeight = (canvas.height * printableWidth) / canvas.width;

      let heightLeft = imageHeight;
      let position = margin;

      pdf.addImage(imageData, 'PNG', margin, position, printableWidth, imageHeight, undefined, 'FAST');
      heightLeft -= printableHeight;

      while (heightLeft > 0) {
        pdf.addPage();
        position = margin - (imageHeight - heightLeft);
        pdf.addImage(imageData, 'PNG', margin, position, printableWidth, imageHeight, undefined, 'FAST');
        heightLeft -= printableHeight;
      }

      const fileName = `relatório-disc-${new Date().toISOString().slice(0, 10)}.pdf`;
      pdf.save(fileName);

      setExported(true);
      setTimeout(() => setExported(false), 2000);
    } catch (error) {
      console.error('Falha ao exportar o relatório em PDF:', error);
    } finally {
      setExporting(false);
    }
  };

  const getConfidenceBadgeColor = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return 'bg-carbon-green-10 text-carbon-green-70 border-carbon-green-50';
      case 'medium':
        return 'bg-carbon-yellow-10 text-carbon-gray-100 border-carbon-yellow-60';
      case 'low':
        return 'bg-carbon-red-10 text-carbon-red-70 border-carbon-red-50';
      default:
        return 'bg-carbon-gray-10 text-carbon-gray-100 border-carbon-gray-50';
    }
  };

  const getDimensionColor = (dimension: string) => {
    switch (dimension) {
      case 'D':
        return 'text-carbon-red-60';
      case 'I':
        return 'text-carbon-yellow-60';
      case 'S':
        return 'text-carbon-green-60';
      case 'C':
        return 'text-carbon-blue-60';
      default:
        return 'text-carbon-gray-100';
    }
  };

  const getDimensionBgColor = (dimension: string) => {
    switch (dimension) {
      case 'D':
        return 'bg-carbon-red-60';
      case 'I':
        return 'bg-carbon-yellow-60';
      case 'S':
        return 'bg-carbon-green-60';
      case 'C':
        return 'bg-carbon-blue-60';
      default:
        return 'bg-carbon-gray-60';
    }
  };

  const matrixRows = orderedDimensions.map((dimension) => {
    const score = result.overall_profile.scores[dimension as keyof typeof result.overall_profile.scores] || 0;
    const avaliacao1 = clampScore(score);
    const avaliacao2 = averageScore;
    const gap = avaliacao1 - avaliacao2;

    return {
      dimension,
      label: getAreaLabel(dimension),
      weight: 25,
      avaliacao1,
      avaliacao2,
      gap,
    };
  });

  return (
    <div className={`w-full bg-white ${exporting ? 'disc-report-exporting' : ''}`} ref={reportRef}>
      <div className="mb-6 flex justify-between items-center gap-5 pb-4 border-b-2 border-carbon-gray-20">
        <div className="flex items-center gap-3">
          <img
            src={logoUrl}
            alt="Liderança Conectada 360 Graus"
            className="h-14 w-auto object-contain"
          />
          <div className="h-10 w-px bg-carbon-yellow-60" aria-hidden="true" />
          <div className="flex items-center gap-2">
            <TrendingUp className="text-carbon-blue-60" size={24} strokeWidth={2.5} />
            <h2 className="text-2xl font-semibold text-carbon-gray-100 tracking-tight">
              Relatório de Análise DISC
            </h2>
          </div>
        </div>
        <button
          onClick={handleExport}
          disabled={exporting}
          data-pdf-ignore="true"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-carbon-blue-60 text-white font-medium hover:bg-carbon-blue-70 transition-colors text-sm"
          aria-label="Exportar relatório em PDF"
        >
          {exported ? (
            <>
              <CheckCheck size={16} strokeWidth={2.5} />
              Exportado!
            </>
          ) : exporting ? (
            <>
              <Download size={16} strokeWidth={2.5} />
              Exportando PDF...
            </>
          ) : (
            <>
              <Download size={16} strokeWidth={2.5} />
              Exportar
            </>
          )}
        </button>
      </div>

      <div className="mb-6 bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
        <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
          Cabeçalho da entrevista
        </h3>
        <div className="space-y-2 text-sm text-carbon-gray-100 leading-relaxed">
          <p>
            <span className="font-semibold">Entrevistador(a): </span>
            {interviewer?.trim() ? interviewer : 'Não informado'}
          </p>
          <p>
            <span className="font-semibold">Entrevistado(a): </span>
            {interviewee?.trim() ? interviewee : 'Não informado'}
          </p>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="pdf-summary-grid mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="pdf-summary-card bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
          <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
            Média geral
          </h3>
          <p className="pdf-metric text-5xl font-bold text-carbon-blue-60 mb-2">
            {averageScore}
          </p>
          <p className="text-sm text-carbon-gray-90 font-medium">de 100</p>
        </div>

        <div className="pdf-summary-card bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
          <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
            Maior dimensão
          </h3>
          <p className={`pdf-metric text-5xl font-bold ${getDimensionColor(highestDimension)} mb-2`}>{highestDimension}</p>
          <p className="text-sm text-carbon-gray-90 font-medium">
            {getDimensionLabel(highestDimension)} ({highestScore})
          </p>
        </div>

        <div className="pdf-summary-card bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
          <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
            Menor dimensão
          </h3>
          <p className={`pdf-metric text-5xl font-bold ${getDimensionColor(lowestDimension)} mb-2`}>{lowestDimension}</p>
          <p className="text-sm text-carbon-gray-90 font-medium">
            {getDimensionLabel(lowestDimension)} ({lowestScore})
          </p>
        </div>

        <div className="pdf-summary-card bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
          <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
            Amplitude
          </h3>
          <p className="pdf-metric text-5xl font-bold text-carbon-blue-60 mb-2">{scoreRange}</p>
          <p className="text-sm text-carbon-gray-90 font-medium">
            diferença entre maior e menor pontuação
          </p>
        </div>
      </div>

      <div className="mb-6 bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <h3 className="text-xs font-semibold text-carbon-gray-70 uppercase tracking-widest">
            Perfil primário e confiança
          </h3>
          <span className={`inline-block px-4 py-2 border-2 text-sm font-bold uppercase tracking-wider ${getConfidenceBadgeColor(result.confidence)}`}>
            Confiança: {getConfidenceLabel(result.confidence)}
          </span>
        </div>
        <div className="mt-3 text-sm text-carbon-gray-100">
          <span className="font-semibold">Perfil identificado:</span> {result.overall_profile.primary} - {getDimensionLabel(result.overall_profile.primary)}
        </div>
      </div>

      {/* Competency Matrix */}
      <div className="mb-6 bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5 overflow-x-auto">
        <h3 className="text-xs font-semibold text-carbon-gray-70 mb-4 uppercase tracking-widest">
          Matriz de competências DISC
        </h3>
        <table className="w-full border-collapse text-sm min-w-[720px]">
          <thead>
            <tr>
              <th className="text-left font-semibold text-carbon-gray-100 bg-carbon-blue-10 border border-carbon-gray-30 p-3">Área comportamental</th>
              <th className="text-center font-semibold text-carbon-gray-100 bg-carbon-blue-10 border border-carbon-gray-30 p-3">Peso</th>
              <th className="text-center font-semibold text-carbon-gray-100 bg-carbon-yellow-10 border border-carbon-gray-30 p-3">Avaliação 1</th>
              <th className="text-center font-semibold text-carbon-gray-100 bg-[#B7DEE8] border border-carbon-gray-30 p-3">Avaliação 2</th>
              <th className="text-center font-semibold text-carbon-gray-100 bg-carbon-blue-10 border border-carbon-gray-30 p-3">GAP</th>
            </tr>
          </thead>
          <tbody>
            {matrixRows.map((row) => (
              <tr key={row.dimension}>
                <td className="border border-carbon-gray-30 p-3 bg-carbon-green-10 font-medium text-carbon-gray-100">
                  <span className="text-carbon-gray-100">({row.dimension})</span>
                  <span className="mx-1">-</span>
                  <span>{row.label}</span>
                </td>
                <td className="border border-carbon-gray-30 p-3 text-center">{row.weight}</td>
                <td className="border border-carbon-gray-30 p-3 text-center bg-carbon-yellow-10 font-semibold">{row.avaliacao1}</td>
                <td className="border border-carbon-gray-30 p-3 text-center bg-[#B7DEE8] font-semibold">{row.avaliacao2}</td>
                <td className={`border border-carbon-gray-30 p-3 text-center font-semibold ${row.gap >= 0 ? 'text-carbon-green-70' : 'text-carbon-red-70'}`}>
                  {row.gap > 0 ? `+${row.gap}` : row.gap}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Method Legend */}
      <div className="mb-6 bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
        <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
          Legenda metodológica
        </h3>
        <ul className="space-y-1 text-sm text-carbon-gray-90 leading-relaxed">
          <li><span className="font-semibold">Peso:</span> distribuição proporcional por dimensão DISC para leitura comparativa.</li>
          <li><span className="font-semibold">Avaliação 1:</span> pontuação da dimensão identificada na entrevista atual.</li>
          <li><span className="font-semibold">Avaliação 2:</span> referência interna baseada na média geral das quatro dimensões.</li>
          <li><span className="font-semibold">GAP:</span> diferença entre a dimensão analisada e a média geral (positiva ou negativa).</li>
        </ul>
      </div>

      {/* DISC Scores */}
      <div className="mb-6 bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
        <h3 className="text-xs font-semibold text-carbon-gray-70 mb-4 uppercase tracking-widest">
          Distribuição de pontuação DISC
        </h3>
        <div className="space-y-4">
          {Object.entries(result.overall_profile.scores).map(([dimension, rawScore]) => {
            const score = clampScore(rawScore);
            return (
              <div key={dimension}>
                <div className="flex justify-between mb-2">
                  <span className={`text-sm font-bold ${getDimensionColor(dimension)} font-ibm-plex-mono uppercase tracking-wider`}>
                    {dimension} - {getDimensionLabel(dimension)}
                  </span>
                  <span className="text-sm font-bold text-carbon-gray-100 font-ibm-plex-mono">{score}</span>
                </div>
                <div className="w-full bg-carbon-gray-20 h-3 relative overflow-hidden">
                  <div
                    className={`h-3 transition-all duration-500 ${getDimensionBgColor(dimension)}`}
                    style={{ width: `${score}%` }}
                  />
                  <div
                    className="absolute top-0 h-full w-0.5 bg-carbon-gray-100 opacity-50"
                    style={{ left: `${score}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary */}
      <div className="mb-6 bg-carbon-blue-10 border-l-4 border-carbon-blue-60 p-5">
        <h3 className="text-xs font-semibold text-carbon-gray-100 mb-3 uppercase tracking-widest">
          Resumo do perfil
        </h3>
        <p className="text-carbon-gray-100 text-sm leading-relaxed">
          {result.overall_profile.summary}
        </p>
      </div>

      {/* Detailed Breakdown */}
      <div className="mb-6 bg-carbon-gray-10 border-l-4 border-carbon-blue-60 p-5">
        <h3 className="text-xs font-semibold text-carbon-gray-70 mb-4 uppercase tracking-widest">
          Análise detalhada
        </h3>
        <div className="space-y-4">
          {result.detailed_breakdown.map((item, index) => (
            <div key={index} className="bg-white p-4 border-l-2 border-carbon-gray-40">
              <div className="flex justify-between items-start mb-2">
                <h4 className={`text-base font-bold ${getDimensionColor(getDimensionByTrait(item.trait))}`}>
                  {item.trait}
                </h4>
                <span className="text-sm font-bold text-carbon-gray-100 font-ibm-plex-mono">
                  {clampScore(item.score)}/100
                </span>
              </div>
              <p className="text-sm text-carbon-gray-90 mb-3 leading-relaxed">
                {item.analysis}
              </p>
              {item.evidence && item.evidence.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-carbon-gray-70 mb-2 uppercase tracking-wider">
                    Evidências:
                  </p>
                  <ul className="space-y-1">
                    {item.evidence.map((quote, idx) => (
                      <li key={idx} className="text-xs text-carbon-gray-90 pl-4 border-l-2 border-carbon-gray-30 italic">
                        "{quote}"
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6 bg-carbon-gray-10 border-l-4 border-carbon-yellow-60 p-5">
        <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
          Ponto prioritário de desenvolvimento
        </h3>
        <p className="text-sm text-carbon-gray-100 leading-relaxed">
          Priorizar o desenvolvimento em <span className="font-semibold">{getDimensionLabel(lowestDimension)}</span>,
          atualmente com pontuação <span className="font-semibold">{lowestScore}/100</span>.
          Recomenda-se um plano prático de evolução com metas semanais, evidências observáveis de comportamento e revisão de progresso a cada ciclo.
        </p>
      </div>

      {/* Recommendations */}
      <div className="mb-6 bg-carbon-green-10 border-l-4 border-carbon-green-60 p-5" data-pdf-ignore="true">
        <h3 className="text-xs font-semibold text-carbon-gray-100 mb-3 uppercase tracking-widest">
          Recomendações de comunicação
        </h3>
        <ul className="space-y-2">
          {result.recommendations.map((rec, index) => (
            <li key={index} className="flex items-start gap-3 text-sm text-carbon-gray-100">
              <span className="text-carbon-green-60 font-bold flex-shrink-0">→</span>
              <span className="leading-relaxed">{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

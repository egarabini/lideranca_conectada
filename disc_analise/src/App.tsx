import { useState } from 'react';
import { AlertCircle, ArrowLeft, Download, RefreshCw, Sparkles } from 'lucide-react';
import { TextAreaInput } from './components/TextAreaInput';
import { ReportDisplay } from './components/ReportDisplay';
import { LoadingSpinner } from './components/LoadingSpinner';
import { useDISCAnalysis, type AnalysisMode } from './hooks/useDISCAnalysis';
import roteiroReadmeMarkdown from '../DISC_ROTEIRO/README.md?raw';
import roteiroInicialMarkdown from '../DISC_ROTEIRO/ROTEIRO-INICIAL-20-PERGUNTAS.md?raw';
import roteiroAlternativoMarkdown from '../DISC_ROTEIRO/ROTEIRO-ALTERNATIVO-20-PERGUNTAS.md?raw';

type RoteiroTipo = 'inicial' | 'alternativo';

function App() {
  const [transcript, setTranscript] = useState('');
  const [interviewer, setInterviewer] = useState('');
  const [interviewee, setInterviewee] = useState('');
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('demo');
  const [roteiroTipo, setRoteiroTipo] = useState<RoteiroTipo>('inicial');
  const { analyze, loading, error, result, clearError, clearResult } = useDISCAnalysis();

  const handleAnalyze = async () => {
    try {
      await analyze(transcript, analysisMode);
    } catch (err) {
      // Error is handled by the hook
    }
  };

  const handleClearAll = () => {
    setTranscript('');
    setInterviewer('');
    setInterviewee('');
    clearResult();
    clearError();
  };

  const downloadMarkdownFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  };

  const handleDownloadRoteiro = () => {
    const roteiroMap: Record<RoteiroTipo, { content: string; filename: string }> = {
      inicial: {
        content: roteiroInicialMarkdown,
        filename: 'ROTEIRO-INICIAL-20-PERGUNTAS.md',
      },
      alternativo: {
        content: roteiroAlternativoMarkdown,
        filename: 'ROTEIRO-ALTERNATIVO-20-PERGUNTAS.md',
      },
    };

    const selected = roteiroMap[roteiroTipo];
    downloadMarkdownFile(selected.content, selected.filename);
  };

  const handleDownloadGuiaRapido = () => {
    downloadMarkdownFile(roteiroReadmeMarkdown, 'README-ROTEIRO-DISC.md');
  };

  return (
    <div className="min-h-screen bg-carbon-gray-10 font-ibm-plex-sans p-4 md:p-6 lg:p-8 xl:p-12">
      <div className="max-w-6xl mx-auto bg-white shadow-carbon-lg border border-carbon-gray-20 p-6 pb-12 sm:p-8 sm:pb-16">
        {/* Header */}
        <div className="mb-10">
          <div className="mb-6 flex justify-between gap-4">
            <a
              href="/"
              className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-carbon-gray-60 hover:text-carbon-blue-60"
              aria-label="Retornar para a página principal"
            >
              <ArrowLeft size={16} strokeWidth={2.5} />
              Retornar
            </a>
          </div>
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-carbon-blue-60 p-2">
              <Sparkles className="text-white" size={28} strokeWidth={2.5} />
            </div>
            <h1 className="font-display text-4xl font-semibold text-carbon-blue-60">
              Analisador de Perfil DISC
            </h1>
          </div>
          <p className="text-base text-carbon-gray-70 max-w-3xl leading-relaxed">
            Analise transcrições de entrevistas para identificar tendências comportamentais DISC.
            Cole uma transcrição abaixo e receba um relatório detalhado sobre estilo de comunicação.
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-carbon-gray-10 p-6 mb-6">
          <div className="mb-6 bg-white border-l-4 border-carbon-yellow-60 p-5">
            <h3 className="text-xs font-semibold text-carbon-gray-70 mb-3 uppercase tracking-widest">
              Roteiro da entrevista
            </h3>
            <p className="text-sm text-carbon-gray-90 mb-4">
              Selecione e baixe o roteiro que será utilizado pelo entrevistador antes de iniciar a entrevista.
            </p>
            <div className="flex flex-col md:flex-row md:items-end gap-4">
              <div className="w-full md:w-80">
                <label htmlFor="roteiro-tipo" className="block mb-2 text-sm font-semibold text-carbon-gray-100 tracking-wide">
                  Tipo de roteiro
                </label>
                <select
                  id="roteiro-tipo"
                  value={roteiroTipo}
                  onChange={(e) => setRoteiroTipo(e.target.value as RoteiroTipo)}
                  className="w-full px-3 py-3 bg-white border-b-2 border-carbon-gray-80 text-carbon-gray-100 focus:border-carbon-yellow-60 focus:outline-none"
                  aria-label="Selecionar tipo de roteiro"
                >
                  <option value="inicial">Roteiro inicial (20 perguntas)</option>
                  <option value="alternativo">Roteiro alternativo (20 perguntas)</option>
                </select>
              </div>
              <button
                onClick={handleDownloadRoteiro}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-carbon-blue-60 text-white font-medium hover:bg-carbon-blue-70 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-carbon-yellow-60"
                aria-label="Baixar roteiro selecionado"
              >
                <Download size={16} strokeWidth={2.5} />
                <span>Baixar roteiro</span>
              </button>
              <button
                onClick={handleDownloadGuiaRapido}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white text-carbon-blue-70 border-2 border-carbon-yellow-60 font-medium hover:bg-carbon-yellow-10 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-carbon-yellow-60"
                aria-label="Baixar guia rápido"
              >
                <Download size={16} strokeWidth={2.5} />
                <span>Baixar guia rápido</span>
              </button>
            </div>
          </div>

          <TextAreaInput
            value={transcript}
            onChange={setTranscript}
            disabled={loading}
          />

          <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="interviewer-input" className="block mb-2 text-sm font-semibold text-carbon-gray-100 tracking-wide">
                Entrevistador(a) (nome e atuação)
              </label>
              <input
                id="interviewer-input"
                type="text"
                value={interviewer}
                onChange={(e) => setInterviewer(e.target.value)}
                disabled={loading}
                placeholder="Ex.: Mônica Motta - Especialista comportamental em ciência aplicada à estratégia e decisão"
                className="w-full px-3 py-3 bg-white border-b-2 border-carbon-gray-80 text-carbon-gray-100 placeholder:text-carbon-gray-50 focus:border-carbon-yellow-60 focus:outline-none disabled:bg-carbon-gray-20 disabled:text-carbon-gray-50"
                aria-label="Entrevistador"
              />
            </div>
            <div>
              <label htmlFor="interviewee-input" className="block mb-2 text-sm font-semibold text-carbon-gray-100 tracking-wide">
                Entrevistado(a) (nome e atuação)
              </label>
              <input
                id="interviewee-input"
                type="text"
                value={interviewee}
                onChange={(e) => setInterviewee(e.target.value)}
                disabled={loading}
                placeholder="Ex.: José Maurício de Souza - Gerente de Recursos Humanos"
                className="w-full px-3 py-3 bg-white border-b-2 border-carbon-gray-80 text-carbon-gray-100 placeholder:text-carbon-gray-50 focus:border-carbon-yellow-60 focus:outline-none disabled:bg-carbon-gray-20 disabled:text-carbon-gray-50"
                aria-label="Entrevistado"
              />
            </div>
          </div>

          {/* Action Bar */}
          <div className="mt-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="w-full md:w-auto">
              <label htmlFor="analysis-mode" className="block mb-2 text-sm font-semibold text-carbon-gray-100 tracking-wide">
                Modo
              </label>
              <select
                id="analysis-mode"
                value={analysisMode}
                onChange={(e) => setAnalysisMode(e.target.value as AnalysisMode)}
                disabled={loading}
                className="w-full md:w-72 px-3 py-3 bg-white border-b-2 border-carbon-gray-80 text-carbon-gray-100 focus:border-carbon-yellow-60 focus:outline-none disabled:bg-carbon-gray-20 disabled:text-carbon-gray-50"
                aria-label="Selecionar modo de análise"
              >
                <option value="demo">Demo</option>
                <option value="openrouter">OpenRouter</option>
                <option value="anthropic">Anthropic</option>
                <option value="gemini">Gemini</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>

            <div className="flex gap-2 justify-end">
              <button
                onClick={handleClearAll}
                disabled={loading}
                className="inline-flex items-center gap-2 px-6 py-3 bg-carbon-gray-10 text-carbon-gray-100 border-2 border-carbon-gray-80 font-medium hover:bg-carbon-gray-20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-carbon-yellow-60"
                aria-label="Limpar entrada e resultado"
              >
                <RefreshCw size={16} strokeWidth={2.5} />
                Limpar
              </button>
              <button
                onClick={handleAnalyze}
                disabled={loading || !transcript.trim()}
                className="inline-flex items-center gap-2 px-6 py-3 bg-carbon-blue-60 text-white font-medium hover:bg-carbon-blue-70 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-carbon-yellow-60"
                aria-label="Analisar transcrição"
              >
                <Sparkles size={16} strokeWidth={2.5} />
                {loading ? 'Analisando...' : 'Analisar'}
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-6 bg-carbon-red-10 border-l-4 border-carbon-red-70 p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-carbon-red-70 flex-shrink-0 mt-0.5" size={20} strokeWidth={2.5} />
                <div className="flex-1">
                  <h3 className="font-semibold text-carbon-gray-100 mb-1 text-sm">Erro</h3>
                  <p className="text-carbon-gray-90 text-sm">{error}</p>
                </div>
                <button
                  onClick={clearError}
                  className="text-carbon-gray-100 hover:text-carbon-gray-70 text-sm font-medium underline"
                  aria-label="Fechar erro"
                >
                  Fechar
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-carbon-gray-10 p-8 mb-6">
            <LoadingSpinner />
          </div>
        )}

        {/* Results Display */}
        {result && !loading && (
          <div className="bg-carbon-gray-10 p-6 pb-8 mb-6">
            <ReportDisplay result={result} interviewer={interviewer} interviewee={interviewee} />
          </div>
        )}

        {/* Footer Info */}
        {!result && !loading && (
          <div className="mt-8 pt-6 border-t-2 border-carbon-gray-20">
            <p className="text-sm text-carbon-gray-70 text-center">
              Modo atual: {analysisMode === 'openrouter' ? 'OpenRouter' : analysisMode === 'anthropic' ? 'Anthropic' : analysisMode === 'gemini' ? 'Gemini' : analysisMode === 'openai' ? 'OpenAI' : 'Demo'} • Recomendado: 150+ palavras para maior confiabilidade
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

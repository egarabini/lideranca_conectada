import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { createReadStream, existsSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import OpenAI from 'openai';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const distDir = join(__dirname, 'dist');
const port = Number(process.env.PORT || 80);
const basicUser = process.env.DISC_BASIC_USER || 'disc';
const basicPassword = process.env.DISC_BASIC_PASSWORD || '';

const DISC_FRAMEWORK = `
Framework DISC para análise comportamental:
- D (Dominância): foco em resultado, decisão e assertividade.
- I (Influência): foco em comunicação, persuasão e relacionamento.
- S (Estabilidade): foco em cooperação, consistência e suporte.
- C (Conformidade): foco em método, qualidade e precisão.
`;

const jsonResponse = (res, status, payload) => {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(payload));
};

const isAuthorized = (req) => {
  if (!basicPassword) {
    return false;
  }

  const header = req.headers.authorization || '';
  if (!header.startsWith('Basic ')) {
    return false;
  }

  const decoded = Buffer.from(header.slice(6), 'base64').toString('utf8');
  const separatorIndex = decoded.indexOf(':');
  if (separatorIndex === -1) {
    return false;
  }

  const user = decoded.slice(0, separatorIndex);
  const password = decoded.slice(separatorIndex + 1);
  return user === basicUser && password === basicPassword;
};

const requireAuth = (req, res) => {
  if (isAuthorized(req)) {
    return true;
  }

  res.writeHead(401, {
    'WWW-Authenticate': 'Basic realm="DISC"',
    'Content-Type': 'text/plain; charset=utf-8',
  });
  res.end('Autenticacao requerida.');
  return false;
};

const readBody = async (req) => {
  const chunks = [];
  let size = 0;

  for await (const chunk of req) {
    size += chunk.length;
    if (size > 300_000) {
      throw new Error('Transcrição muito grande.');
    }
    chunks.push(chunk);
  }

  return Buffer.concat(chunks).toString('utf8');
};

const stripJsonFence = (text) => {
  const trimmed = text.trim();
  if (!trimmed.startsWith('```')) {
    return trimmed;
  }

  return trimmed.replace(/^```(?:json)?/i, '').replace(/```$/i, '').trim();
};

const parseDiscResult = (content) => {
  const parsed = JSON.parse(stripJsonFence(content));

  if (!parsed.overall_profile || !parsed.detailed_breakdown) {
    throw new Error('Formato de resposta inválido da API.');
  }

  return parsed;
};

const buildPrompt = (transcript) => `FRAMEWORK
***
${DISC_FRAMEWORK}

TRANSCRIÇÃO
***
${transcript}

TAREFA: Conclua a análise DISC seguindo a estrutura do framework com precisão.
Atribua pontuação de 1 a 100 para cada traço. Forneça citações de evidência.
Todos os textos de saída devem estar em português (pt-BR).

Schema JSON de saída:
{
  "overall_profile": {
    "primary": "D/I/S/C",
    "secondary": "D/I/S/C",
    "scores": {"D": number, "I": number, "S": number, "C": number},
    "summary": "resumo do perfil em 2 frases"
  },
  "detailed_breakdown": [
    {"trait": "Dominância", "score": number, "evidence": ["citação1", "citação2"], "analysis": "1-2 frases"},
    {"trait": "Influência", "score": number, "evidence": ["citação1", "citação2"], "analysis": "1-2 frases"},
    {"trait": "Estabilidade", "score": number, "evidence": ["citação1", "citação2"], "analysis": "1-2 frases"},
    {"trait": "Conformidade", "score": number, "evidence": ["citação1", "citação2"], "analysis": "1-2 frases"}
  ],
  "recommendations": ["recomendação1", "recomendação2", "recomendação3"],
  "confidence": "high/medium/low"
}`;

const analyzeWithOpenAICompatible = async ({ transcript, mode }) => {
  const isOpenRouter = mode === 'openrouter';
  const apiKey = isOpenRouter
    ? process.env.OPENROUTER_API_KEY || process.env.VITE_OPENROUTER_API_KEY
    : process.env.OPENAI_API_KEY || process.env.VITE_OPENAI_API_KEY;

  if (!apiKey) {
    throw new Error(`Chave de API para ${isOpenRouter ? 'OpenRouter' : 'OpenAI'} não configurada no servidor.`);
  }

  const client = new OpenAI({
    apiKey,
    baseURL: isOpenRouter ? 'https://openrouter.ai/api/v1' : undefined,
    defaultHeaders: isOpenRouter ? { 'X-Title': 'DISC Profile Analyzer' } : undefined,
  });

  const model = isOpenRouter
    ? process.env.OPENROUTER_MODEL || process.env.VITE_OPENROUTER_MODEL || 'openai/gpt-4o-mini'
    : process.env.OPENAI_MODEL || process.env.VITE_OPENAI_MODEL || 'gpt-4o-mini';

  const completion = await client.chat.completions.create({
    model,
    messages: [
      { role: 'system', content: 'Você é um especialista em avaliação comportamental DISC. Retorne APENAS JSON válido em português (pt-BR).' },
      { role: 'user', content: buildPrompt(transcript) },
    ],
    temperature: 0.1,
    max_tokens: 4000,
    response_format: { type: 'json_object' },
  });

  return parseDiscResult(completion.choices[0]?.message?.content || '');
};

const analyzeWithGemini = async ({ transcript }) => {
  const apiKey = process.env.GEMINI_API_KEY || process.env.VITE_GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error('Chave de API para Gemini não configurada no servidor.');
  }

  const model = process.env.GEMINI_MODEL || process.env.VITE_GEMINI_MODEL || 'gemini-1.5-flash';
  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent?key=${encodeURIComponent(apiKey)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: `Você é um especialista em avaliação comportamental DISC. Retorne APENAS JSON válido em português (pt-BR).\n\n${buildPrompt(transcript)}` }] }],
      generationConfig: { temperature: 0.1, maxOutputTokens: 4000 },
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload?.error?.message || 'Erro ao chamar Gemini.');
  }

  return parseDiscResult(payload?.candidates?.[0]?.content?.parts?.[0]?.text || '');
};

const analyzeWithAnthropic = async ({ transcript }) => {
  const apiKey = process.env.ANTHROPIC_API_KEY || process.env.VITE_ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('Chave de API para Anthropic não configurada no servidor.');
  }

  const model = process.env.ANTHROPIC_MODEL || process.env.VITE_ANTHROPIC_MODEL || 'claude-3-5-haiku-latest';
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model,
      max_tokens: 4000,
      temperature: 0.1,
      system: 'Você é um especialista em avaliação comportamental DISC. Retorne APENAS JSON válido em português (pt-BR).',
      messages: [{ role: 'user', content: buildPrompt(transcript) }],
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload?.error?.message || 'Erro ao chamar Anthropic.');
  }

  return parseDiscResult(payload?.content?.map((part) => part.text || '').join('\n') || '');
};

const handleAnalyze = async (req, res) => {
  try {
    const body = JSON.parse(await readBody(req));
    const transcript = String(body.transcript || '').trim();
    const mode = String(body.mode || '');

    if (!transcript) {
      return jsonResponse(res, 400, { error: 'Insira uma transcrição para analisar.' });
    }

    if (!['openai', 'openrouter', 'gemini', 'anthropic'].includes(mode)) {
      return jsonResponse(res, 400, { error: 'Modo de análise inválido.' });
    }

    const result = mode === 'gemini'
      ? await analyzeWithGemini({ transcript })
      : mode === 'anthropic'
        ? await analyzeWithAnthropic({ transcript })
        : await analyzeWithOpenAICompatible({ transcript, mode });

    return jsonResponse(res, 200, result);
  } catch (error) {
    return jsonResponse(res, 500, { error: error instanceof Error ? error.message : 'Erro desconhecido.' });
  }
};

const contentTypeByExtension = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

const serveStatic = async (req, res) => {
  const url = new URL(req.url || '/', 'http://localhost');

  if (url.pathname === '/disc') {
    res.writeHead(301, { Location: '/disc/' });
    res.end();
    return;
  }

  let relativePath = decodeURIComponent(url.pathname.replace(/^\/disc\/?/, ''));
  if (!relativePath || relativePath.endsWith('/')) {
    relativePath = 'index.html';
  }

  const requestedPath = normalize(join(distDir, relativePath));
  const filePath = requestedPath.startsWith(distDir) && existsSync(requestedPath)
    ? requestedPath
    : join(distDir, 'index.html');

  const contentType = contentTypeByExtension[extname(filePath)] || 'application/octet-stream';
  res.writeHead(200, { 'Content-Type': contentType });
  createReadStream(filePath).pipe(res);
};

createServer(async (req, res) => {
  if (!req.url?.startsWith('/disc')) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }

  if (!requireAuth(req, res)) {
    return;
  }

  if (req.method === 'POST' && req.url === '/disc/api/analyze') {
    await handleAnalyze(req, res);
    return;
  }

  if (req.method === 'GET' || req.method === 'HEAD') {
    await serveStatic(req, res);
    return;
  }

  res.writeHead(405);
  res.end('Method not allowed');
}).listen(port, () => {
  console.log(`DISC server listening on ${port}`);
});

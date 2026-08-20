# lideranca_conectada
Liderança Conectada 360 Graus

## Desenvolvimento e deploy com Docker

Copie o arquivo de exemplo de ambiente e ajuste as senhas:

```bash
cp .env.example .env
```

Suba a aplicação e o banco:

```bash
docker compose up -d --build
```

A aplicação fica disponível em `http://localhost:8000`.
O endpoint `GET /health` valida a aplicação e a conexão com o PostgreSQL.

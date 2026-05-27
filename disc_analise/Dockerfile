FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY server.mjs ./
COPY --from=build /app/dist ./dist

EXPOSE 80

CMD ["node", "server.mjs"]

FROM node:20-alpine

WORKDIR /app

COPY package.json ./
ENV CI=true
RUN npm install --no-audit --no-fund

COPY . .

EXPOSE 5173

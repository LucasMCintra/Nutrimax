FROM node:18-alpine

WORKDIR /app

COPY frontend/package.json ./package.json
RUN npm install

COPY frontend ./frontend

WORKDIR /app/frontend

EXPOSE 3000

CMD ["npm", "start"]

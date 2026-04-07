# ./api-frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY app/package*.json ./
RUN npm install

COPY app .

# Produkcyjna wersja (jeśli chcesz `npm run build`)
# RUN npm run build
# CMD ["npx", "serve", "dist"]

# Dev wersja
CMD ["npm", "run", "dev"]
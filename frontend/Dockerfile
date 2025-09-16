FROM node:20 AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 5173

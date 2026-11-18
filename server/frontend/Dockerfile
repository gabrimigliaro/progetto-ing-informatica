# Stage 1: Compilazione della build statica React
FROM node:22-slim AS build
WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

ARG VITE_VAPID_PUBLIC_KEY
ENV VITE_VAPID_PUBLIC_KEY=$VITE_VAPID_PUBLIC_KEY

RUN npm run build

# Stage 2: Servizio dei file statici tramite Nginx interno sulla porta 80
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

RUN printf 'server {\n\
    listen 80;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location = /sw.js {\n\
        add_header Cache-Control "no-cache, no-store, must-revalidate";\n\
        try_files $uri =404;\n\
    }\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
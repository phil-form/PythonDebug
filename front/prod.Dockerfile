# Build
FROM node:24-slim AS build

WORKDIR /front

# Copie le packge.json & packge.lock.json dans /front
COPY package*.json ./

RUN npm i

# Copie du dossier courant dans /front
COPY . .

RUN npm run build

# Prod
FROM nginx:latest as prod

COPY --from=build /front/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
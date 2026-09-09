# 1. Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
# Construye la aplicación estática
RUN npm run build

# 2. Production stage (Nginx)
FROM nginx:alpine
# Copia la app construida al directorio html de Nginx
COPY --from=build /app/build /usr/share/nginx/html
# Expone el puerto 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Stage 1 — build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .
RUN npm run build

# Stage 2 — serve
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
# Override default server block to support React Router client-side routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

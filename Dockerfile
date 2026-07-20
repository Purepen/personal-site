# Static site, no build step. nginx serves the files directly.
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80

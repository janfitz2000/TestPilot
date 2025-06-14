FROM nginx:alpine

# Copy the static files
COPY web-static/ /usr/share/nginx/html/

# Add custom nginx config
RUN echo 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    add_header "Access-Control-Allow-Origin" "*";\n\
    add_header "Access-Control-Allow-Methods" "GET, POST, OPTIONS";\n\
    add_header "Access-Control-Allow-Headers" "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range";\n\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

FROM debian:bullseye

RUN apt-get update && apt-get install -y nginx openssl && rm -rf /var/lib/apt/lists/*

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/inception.key \
    -out /etc/nginx/inception.crt \
    -subj "/C=FR/ST=Paris/L=Paris/O=42/CN=ylau-sim.42.fr"

COPY conf/nginx.conf /etc/nginx/sites-available/default

CMD ["nginx", "-g", "daemon off;"]

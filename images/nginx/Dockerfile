FROM nginx:1.19

RUN mkdir -p /etc/nginx/includes \
 && mkdir -p /etc/nginx/conf.d \
 && mkdir -p /etc/nginx/logs \
 && touch /etc/nginx/logs/access.log

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./proxy.conf   /etc/nginx/includes/proxy.conf

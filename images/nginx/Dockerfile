FROM nginx:1.19

RUN mkdir -p /etc/nginx/includes && mkdir -p /etc/nginx/conf.d

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./proxy.conf   /etc/nginx/includes/proxy.conf

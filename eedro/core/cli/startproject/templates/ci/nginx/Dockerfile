FROM nginx:1.27

RUN rm -rf /etc/nginx/templates/* \
    && rm -rf /etc/nginx/conf.d/*

COPY ci/nginx/templates /etc/nginx/templates

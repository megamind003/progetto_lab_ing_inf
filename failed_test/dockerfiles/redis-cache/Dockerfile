FROM redis:alpine

COPY redis.conf /usr/local/etc/redis/redis.conf
RUN mkdir -p /var/log/redis && chmod 777 /var/log/redis
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
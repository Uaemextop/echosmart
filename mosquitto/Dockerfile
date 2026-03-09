FROM eclipse-mosquitto:2.0

# Copy configuration
COPY config/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]

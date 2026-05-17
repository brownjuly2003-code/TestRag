FROM python:3.13-alpine
WORKDIR /app
COPY main.py .
# Persist offset across restarts; volume-mountable via docker-compose.
RUN mkdir -p /var/lib/tg-poll-bridge && chown nobody:nobody /var/lib/tg-poll-bridge
USER nobody
ENTRYPOINT ["python", "-u", "main.py"]

FROM python:3.11-slim

# Necesario para "ip" que Kolibri usa al iniciar
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir kolibri==0.16.*
RUN useradd -m kolibri
USER kolibri
WORKDIR /home/kolibri
VOLUME ["/home/kolibri/.kolibri"]
EXPOSE 8080
CMD ["kolibri","start","--foreground"]


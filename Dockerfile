# Railway all-in-one: OpenSERP (Chromium) + FastAPI in one container.
# Avoids Railway private IPv6 (.railway.internal) which cannot reach IPv4-only OpenSERP.
FROM karust/openserp:latest

USER root

COPY openserp/chrome-wrapper.sh /usr/local/bin/chrome-wrapper
COPY start.sh /usr/local/bin/start.sh
RUN chmod 0755 /usr/local/bin/chrome-wrapper /usr/local/bin/start.sh \
 && ln -sf /usr/local/bin/openserp /usr/bin/openserp \
 && apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY api/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt \
 || pip3 install --no-cache-dir -r /app/requirements.txt

COPY api/ /app/
COPY --chown=chrome:chrome config.yaml /usr/src/app/config.yaml
RUN chown -R chrome:chrome /app

ENV OPENSERP_APP_BROWSER_PATH=/usr/local/bin/chrome-wrapper \
    OPENSERP_SERVER_HOST=127.0.0.1 \
    OPENSERP_SERVER_PORT=7000 \
    OPENSERP_BASE_URL=http://127.0.0.1:7000 \
    COMBINED_OPENSERP=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

USER chrome

EXPOSE 8000

# Parent image ENTRYPOINT is ["openserp"]. Without this reset, Railway/Docker
# runs `openserp /usr/local/bin/start.sh` and OpenSERP rejects the unknown command.
ENTRYPOINT ["/bin/sh", "/usr/local/bin/start.sh"]
CMD []

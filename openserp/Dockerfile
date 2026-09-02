# Custom OpenSERP image for Railway: same official binary, Chrome launched without the
# Linux sandbox (required on Railway; credentials.cc Permission denied otherwise).
FROM karust/openserp:latest

USER root

COPY openserp/chrome-wrapper.sh /usr/local/bin/chrome-wrapper
RUN chmod 0755 /usr/local/bin/chrome-wrapper

ENV OPENSERP_APP_BROWSER_PATH=/usr/local/bin/chrome-wrapper

USER chrome

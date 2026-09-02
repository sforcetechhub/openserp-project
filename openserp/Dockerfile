# Custom OpenSERP image for Railway: same official binary, Chrome launched without the
# Linux sandbox (required on Railway; credentials.cc Permission denied otherwise).
FROM karust/openserp:latest

USER root

COPY openserp/chrome-wrapper.sh /usr/local/bin/chrome-wrapper
RUN chmod 0755 /usr/local/bin/chrome-wrapper \
 && ln -sf /usr/local/bin/openserp /usr/bin/openserp

ENV OPENSERP_APP_BROWSER_PATH=/usr/local/bin/chrome-wrapper \
    PATH="/usr/local/bin:/usr/bin:${PATH}"

USER chrome

# Railway custom start commands replace ENTRYPOINT and often have a short PATH.
# Bake the server command in so the start command can be left empty.
ENTRYPOINT ["/usr/local/bin/openserp"]
CMD ["serve", "-a", "0.0.0.0", "-p", "7000"]

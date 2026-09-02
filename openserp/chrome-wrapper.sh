#!/bin/sh
# Chromium's user-namespace sandbox is blocked on Railway (credentials.cc Permission denied).
exec /headless-shell/headless-shell \
  --no-sandbox \
  --disable-setuid-sandbox \
  --disable-dev-shm-usage \
  --disable-gpu \
  --no-zygote \
  "$@"

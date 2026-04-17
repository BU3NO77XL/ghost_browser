#!/usr/bin/env bash
set -euo pipefail

is_enabled() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

export DISPLAY="${DISPLAY:-:99}"
XVFB_WHD="${XVFB_WHD:-1920x1080x24}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"

mkdir -p /data/profiles /data/output /data/storage

if is_enabled "${GHOST_ENABLE_NOVNC:-true}"; then
  rm -f "/tmp/.X${DISPLAY#:}-lock"

  Xvfb "${DISPLAY}" -screen 0 "${XVFB_WHD}" -nolisten tcp >/tmp/xvfb.log 2>&1 &
  sleep 1

  fluxbox >/tmp/fluxbox.log 2>&1 &

  x11vnc \
    -display "${DISPLAY}" \
    -forever \
    -shared \
    -localhost \
    -nopw \
    -rfbport "${VNC_PORT}" \
    >/tmp/x11vnc.log 2>&1 &

  websockify \
    --web=/usr/share/novnc \
    "0.0.0.0:${NOVNC_PORT}" \
    "127.0.0.1:${VNC_PORT}" \
    >/tmp/novnc.log 2>&1 &

  echo "noVNC listening on port ${NOVNC_PORT}; DISPLAY=${DISPLAY}"
fi

exec "$@"

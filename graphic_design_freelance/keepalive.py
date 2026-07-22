"""
Keep-alive self-pinger for Render's free tier.

Render free web services spin down after ~15 minutes with no inbound traffic,
which causes a slow (~50s) cold start on the next visit. This starts a daemon
thread that periodically requests the service's own public URL, which counts as
inbound traffic and resets the idle timer so the service never sleeps.

It only runs on Render (RENDER_EXTERNAL_HOSTNAME is set there) and can be turned
off with KEEPALIVE_DISABLED=1. The interval is configurable via
KEEPALIVE_INTERVAL_SECONDS.
"""

import logging
import os
import threading
import time
from urllib.request import urlopen

logger = logging.getLogger(__name__)

# Render's idle window is ~15 min (900s). Default to 14 min so there's a safe
# margin - pinging with only a few seconds to spare risks the service sleeping
# if a single ping is delayed. Override with KEEPALIVE_INTERVAL_SECONDS.
DEFAULT_INTERVAL_SECONDS = 840

_started = False
_lock = threading.Lock()


def _ping_loop(url, interval):
    while True:
        time.sleep(interval)
        try:
            with urlopen(url, timeout=30) as resp:
                resp.read(1)
            logger.info("keep-alive ping ok (%s)", url)
        except Exception as exc:  # never let a failed ping kill the thread
            logger.warning("keep-alive ping failed (%s): %s", url, exc)


def start_keepalive():
    """Start the self-ping thread once, only when running on Render."""
    global _started

    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not host:
        return  # not on Render (e.g. local dev) - nothing to keep alive
    if os.environ.get("KEEPALIVE_DISABLED"):
        return

    with _lock:
        if _started:
            return
        _started = True

    try:
        interval = int(os.environ.get("KEEPALIVE_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS))
    except ValueError:
        interval = DEFAULT_INTERVAL_SECONDS

    url = f"https://{host}/"
    thread = threading.Thread(
        target=_ping_loop, args=(url, interval), name="keepalive", daemon=True
    )
    thread.start()
    logger.info("keep-alive started: pinging %s every %ss", url, interval)

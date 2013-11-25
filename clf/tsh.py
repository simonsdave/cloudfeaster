"""Super simple module that's only purpose in life is to install a
SIGTERM handler that writes a message to the logging infrastructure
before the application terminates."""

import signal
import sys
import logging


_logger = logging.getLogger("CLF_%s" % __name__)


def _term_signal_handler(signalNumber, frame):
    assert signalNumber == signal.SIGTERM
    _logger.error("Shutting down ...")
    sys.exit(0)


def install():
    """Install this module's SIGTERM handler."""
    signal.signal(signal.SIGTERM, _term_signal_handler)

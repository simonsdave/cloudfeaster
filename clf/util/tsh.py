"""Super simple module that's only purpose in life is to install a
SIGINT handler that writes a message to the logging infrastructure
before the application terminates.
"""

import signal
import sys
import logging

_logger = logging.getLogger(__name__)


def _term_signal_handler(signalNumber, frame):
    assert signalNumber == signal.SIGINT
    _logger.info("Shutting down ...")
    sys.exit(0)


def install():
    """Install this module's SIGINT handler."""
    signal.signal(signal.SIGINT, _term_signal_handler)

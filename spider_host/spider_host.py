#!/usr/bin/env python
"""This module is the spider host's mainline."""

import logging

from clparser import CommandLineParser
import pumper


_logger = logging.getLogger("CLF_%s" % __name__)


if __name__ == "__main__":
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    logging.basicConfig(level=clo.logging_level)

    fmt = (
        "Spider Host "
        "reading requests from queue '{clo.request_queue_name}', "
        "writing responses to queue '{clo.response_queue_name}' "
        "and sleeping {clo.min_num_secs_to_sleep} to "
        "{clo.max_num_secs_to_sleep} seconds"
    )
    _logger.info(fmt.format(clo=clo))

    pumper.pump(
        clo.request_queue_name,
        clo.response_queue_name,
        clo.min_num_secs_to_sleep,
        clo.max_num_secs_to_sleep)

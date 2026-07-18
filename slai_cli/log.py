"""Logging setup for SLAI CLI."""

import logging
import sys


def setup_logging(verbose=False, debug=False):
    """Configure logging based on verbosity."""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


logger = logging.getLogger("slai")

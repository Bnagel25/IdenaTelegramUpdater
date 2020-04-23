import logging
import os
import json

from twisted.internet import reactor
from twisted.logger import (
    globalLogBeginner,
    STDLibLogObserver,
    FilteringLogObserver,
    LogLevelFilterPredicate,
    LogLevel,
)

from idenaTelegramUpdater import context, worker

HOME = "/home"

logger = logging.getLogger(__name__)


def _identify_pass(response, work):
    """ Callback for idendify, on success: start the normal process  """
    res = json.loads(response)
    if "result" not in res and "address" not in res["result"]:
        logger.info("Identity Not Found!")
        return

    logger.info(
        "Identity found {}: {}".format(res["result"]["state"], res["result"]["address"])
    )
    work.load_today()


def _identify_fail(failure):
    """ On failure, print error and return """
    logger.warning(failure.getErrorMessage())
    logger.warning("Failed to setup & obtain identity")
    return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    filtering = FilteringLogObserver(
        STDLibLogObserver(), [LogLevelFilterPredicate(defaultLogLevel=LogLevel.warn)]
    )
    globalLogBeginner.beginLoggingTo([filtering])

    ctx = context.init_context(HOME, reactor)
    work = worker.Worker(ctx)

    d = work.setup()
    d.addCallbacks(_identify_pass, _identify_fail, callbackArgs=(work,))
    reactor.run()

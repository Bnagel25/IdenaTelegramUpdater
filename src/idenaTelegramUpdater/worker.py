import logging
import json
from datetime import datetime, timedelta

import attr
from twisted.internet import defer

from idenaTelegramUpdater import idena, telegramWrapper, context


logger = logging.getLogger(__name__)
VALIDATION_FMT = "%Y-%m-%dT%H:%M:00Z"

@attr.s
class Worker:
    ctx = attr.ib()
    _idena = attr.ib(default=None)
    _tele = attr.ib(default=None)
    _alerts = attr.ib(default=None)
    _epoch_alert_armed = attr.ib(default=False)

    def setup(self):
        """
        Setup for worker.

        Returns Idena identity deferred
        """
        logger.info("Initializing worker setup")
        self._idena = idena.Idena(self.ctx)
        self._tele = telegramWrapper.TelegramWrapper(self.ctx)
        try:
            self._idena.setup()
            self._tele.setup()
            return self._idena.identify()
        except Exception as e:
            return defer.fail(Exception(e))

    def load_today(self):
        """
        Loads today's alert times into reactor queue

        Also check's for Epoch configuration, and set's that timer as well
        """
        self._alerts = []
        now = datetime.utcnow()
        for aT in self.ctx.config.alertTimes:
            logger.info("Alerting @ {}".format(aT))
            alert = datetime.strptime(aT, context.TIME_FORMAT)
            time_today = datetime(now.year, now.month, now.day, alert.hour, alert.minute, alert.second)
            time_until = int((time_today - now).total_seconds())
            if time_until > 0:
                logger.info("Loading {} today".format(aT))
                self._alerts.append(aT)
                self.ctx.reactor.callLater(time_until, self, aT)

        if self.ctx.config.alertForEpoch and not self._epoch_alert_armed:
            self._epoch_alert_armed = True
            self._queue_epoch_alert()

    def load_tomorrow(self):
        """
        Loads tomorrow's alert times into reactor queue
        """
        self._alerts = []
        now = datetime.utcnow()
        for aT in self.ctx.config.alertTimes:
            alert = datetime.strptime(aT, context.TIME_FORMAT)
            time_tomorrow = datetime(
                now.year,
                now.month,
                now.day,
                alert.hour,
                alert.minute,
                alert.second
            ) + timedelta(days=1)
            time_until = int((time_tomorrow - now).total_seconds())
            if time_until > 0:
                logger.info("Loading {} tomorrow".format(aT))
                self._alerts.append(aT)
                self.ctx.reactor.callLater(time_until, self, aT)

        if self.ctx.config.alertForEpoch and not self._epoch_alert_armed:
            self._epoch_alert_armed = True
            self._queue_epoch_alert()

    def _err(self, err):
        logger.warning(err.getErrorMessage())
        return

    def _epoch_cb(self, response):
        """ Response for epoch """
        res = json.loads(response)
        if "result" not in res and "nextValidation" not in res["result"]:
            logger.info("Next validation not found")
            return

        next_validation = res["result"]["nextValidation"]
        logger.info("Next validation is {}, setting an alert for 30 min prior".format(next_validation))
        now = datetime.utcnow()
        alert_time = datetime.strptime(next_validation, VALIDATION_FMT) - timedelta(minutes=30)
        time_until = int((alert_time - now).total_seconds())
        self.ctx.reactor.callLater(time_until, self._send_epoch_alert)

    def _queue_epoch_alert(self):
        """ Get's the next Epoch time, and sets an alarm for 30min prior"""
        d = self._idena.epoch()
        d.addCallbacks(self._epoch_cb, self._err)
        return d

    def _send_epoch_alert(self):
        """ Send alert for upcoming validation session """
        logger.info("Alerting for upcoming validation session")
        self._epoch_alert_armed = False
        self._tele.send_validation_alert()

    def _balance_cb(self, response):
        """
        Callback for balance deferred.
        If balance found, a telegram message is sent.
        Else return None
        """
        res = json.loads(response)
        if "result" not in res and "balance" not in res["result"]:
            logger.info("Balance Not Found!")
            return

        logger.info(
            "Balance found stake={}: balance={}".format(
                float(res["result"]["stake"]), float(res["result"]["balance"])
            )
        )

        self._tele.send_balance(
            float(res["result"]["balance"]), float(res["result"]["stake"])
        )

    def _balance_err(self, failure):
        """ Balance errBack, print failure and return"""
        logger.warning("Failed to get balance")
        logger.warning(failure.getErrorMessage())
        return

    def __call__(self, time):
        """ Call balance and send a telegram-message """
        self._alerts.remove(time)
        if len(self._alerts) == 0:
            logger.info("Reloading Tomorrow")
            self.load_tomorrow()

        d = self._idena.balance()
        d.addCallbacks(self._balance_cb, self._balance_err)
        return

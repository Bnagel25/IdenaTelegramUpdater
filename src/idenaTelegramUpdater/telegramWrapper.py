import logging
import json

import attr
import telegram


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60


@attr.s
class TelegramWrapper:
    ctx = attr.ib()
    _bot = attr.ib(default=None)
    _prevTotalBalance = attr.ib(default=None)

    def setup(self):
        """ Setup the Telegram Bot for use """
        if self.ctx.config.telegramToken == "":
            raise Exception("TelegramToken is empty")

        if self.ctx.config.telegramChatId == "":
            raise Exception("TelegramChatId is empty")

        request = telegram.utils.request.Request(read_timeout=DEFAULT_TIMEOUT)
        self._bot = telegram.Bot(self.ctx.config.telegramToken, request=request)
        return True

    def send_balance(self, balance, stake):
        """ Sends balance information via telegram bot """
        message = """Current Total Balance: *{:0.3f}*""".format(
            (balance + stake)
        )
        if self._prevTotalBalance:
            balanceDiff = (balance + stake) - (self._prevTotalBalance)
            message += """\nBalance Diff: *{:0.3f}*""".format(balanceDiff)
        self._prevTotalBalance = balance + stake
        return self._bot.send_message(
            chat_id=self.ctx.config.telegramChatId, text=message, parse_mode="markdown"
        )

    def send_validation_alert(self):
        """ Sends alert for upcoming validation via telegram bot """
        message = "*UPCOMING VALIDATION SESSION ALERT*"
        return self._bot.send_message(
            chat_id=self.ctx.config.telegramChatId, text=message, parse_mode="markdown"
        )

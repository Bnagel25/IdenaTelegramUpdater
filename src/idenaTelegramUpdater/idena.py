import logging
import json

import treq
import attr

logger = logging.getLogger(__name__)

IDENTIFY = "dna_identity"
BALANCE = "dna_getBalance"
EPOCH = "dna_epoch"


@attr.s
class Idena:
    ctx = attr.ib()

    def setup(self):
        """ Returns true if all fields valid, else throws """
        if self.ctx.config.nodeApiKey == "":
            raise Exception("Node API Key is empty")

        if self.ctx.config.nodeAddress == "":
            raise Exception("Node Address is empty")

        return True


    def _build_payload(self, method):
        """ Builds the POST body """
        return {
            "key": self.ctx.config.nodeApiKey,
            "method": method,
            "params": [self.ctx.config.nodeAddress],
            "id": 1,
        }

    def _post(self, payload):
        """
        Posts request through twisted agent.

        Returns deferred
        """
        url = "http://{}:{}".format(
            self.ctx.config.nodeHost, self.ctx.config.nodePort
        ).encode("utf-8")
        d = treq.post(
            url,
            json.dumps(payload).encode("ascii"),
            headers={b"Content-Type": [b"application/json"],
                     b"User-Agent": [b"API"]},
        )
        return d

    def identify(self):
        """
        Send post request for identity provided

        Return deferred
        """
        d = self._post(self._build_payload(IDENTIFY))
        d.addCallback(treq.text_content)
        return d

    def balance(self):
        """
        Send post request for balance

        Return deferred
        """
        d = self._post(self._build_payload(BALANCE))
        d.addCallback(treq.text_content)
        return d

    def epoch(self):
        """
        Send post request for epoch

        Return deferred
        """
        d = self._post(self._build_payload(EPOCH))
        d.addCallback(treq.text_content)
        return d

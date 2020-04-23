# Idena Telegram Updater

Idena Telegram Updater is a python daemon that is intended to run along-side a VPS instance of an Idena Node.
It provides updates and alerts on a configurable schedule via a Telegram Bot. Runs on Python3 and the Twisted async framework.

This assumes that you have:
- A Telegram bot token and chatId previously set
- A running Idena Node with a wallet and an APIKey

# Configuration
Configure using `sample-config.json` file.
```
{
    "nodeAddress": "", <- Idena Node Address
    "nodeApiKey": "", <- Idena Node ApiKey
    "nodeHost": "localhost", <- Idena Host Addresss (leave out HTTP)
    "nodePort": "9009", <- Idena Host Port
    "telegramToken": "", <- Telegram Bot token
    "telegramChatId": "", <- Telegram Bot ChatId
    "alertTimes": [], <- Alert Time in %H:%M:%S format
    "alertForEpoch": true <- If true will alert 30 minutes before upcoming validation
}
```
Place at `/home` and name it `idenaTelegramUpdater-config.json`

Any configuration change needs the service to be restarted before the changes are affected.

# Installation
Take a `.whl` file from `/releases` and scp onto your machine.
If running a clean instance of a VPS, it may require you to install pip3.
Do so by running:
``` shell
sudo apt-get install python3-pip
```

Install the whl to pip3 via command
``` shell
pip3 install idenaTelegramUpdater-<version>.whl
```
After installation: 
1. Move the `idenaTelegramUpdaterd.service` to `/etc/systemd/system/`
2. Run `systemctl daemon-reload` to reload the service file
3. Run `systemctl restart idenaTelegramUpdaterd` to start the file

# Restarting the Service
Restart using command
```
systemctl restart idenaTelegramUpdaterd
```

# Output
Monitor output via 
```
journalctl -fu idenaTelegramUpdaterd
```

Output, if configured properly, will look similar to:
```
Apr 23 02:43:15 Idena-Server systemd[1]: Started Idena Telegram Updating Daemon.
Apr 23 02:43:16 Idena-Server python3[3027]: INFO:idenaTelegramUpdater.worker:Initializing worker setup
Apr 23 02:43:17 Idena-Server python3[3027]: INFO:__main__:Identity found <state>: <address>
Apr 23 02:43:17 Idena-Server python3[3027]: INFO:idenaTelegramUpdater.worker:Alerting @ 03:00:00
Apr 23 02:43:17 Idena-Server python3[3027]: INFO:idenaTelegramUpdater.worker:Alerting @ 15:00:00
Apr 23 02:43:17 Idena-Server python3[3027]: INFO:idenaTelegramUpdater.worker:Alerting @ 19:00:00
Apr 23 02:43:17 Idena-Server python3[3027]: INFO:idenaTelegramUpdater.worker:Alerting @ 23:00:00
Apr 23 02:43:17 Idena-Server python3[3027]: INFO:idenaTelegramUpdater.worker:Next validation is 2020-05-04T13:30:00Z, setting an alert for 30 min prior
Apr 23 02:59:59 Idena-Server python3[3027]: INFO:idenaTelegramUpdater.worker:Balance found stake=<stake>: balance=<balance>
```

import datetime
import time
from datetime import datetime

import arrow
import dateutil.parser
import pytz
import requests
import urllib3
from dateutil import tz
from discord_hooks import Webhook

urllib3.disable_warnings()
monitor  = True
productName = None
lookForSoldOut = None
webhookUrls = [""]
goatSurpriseUrl = "https://carnival-api.goat.com/api/contest/surprise_drops"
auth = {"authorization":'Token token=""'}
from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/New_York')
while monitor == True:
    r = requests.get(goatSurpriseUrl, headers=auth)
    data = r.json()
    goatData = data["data"]
    productUrl = "https://www.goat.com/sneakers/{}".format(goatData["product"]["slug"])
    d = datetime.now(pytz.timezone("America/New_York"))
    logTime = d.strftime("%I:%M:%S %p %Z")

    utcStart = datetime.strptime(goatData["startTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
    utcStart = utcStart.replace(tzinfo=from_zone)
    startDt = utcStart.astimezone(to_zone)
    startTime = startDt.strftime("%m/%d %I:%M:%S %p %Z")

    utcEnd = datetime.strptime(goatData["endTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
    utcEnd = utcEnd.replace(tzinfo=from_zone)
    endDt = utcEnd.astimezone(to_zone)
    endTime = endDt.strftime("%m/%d %I:%M:%S %p %Z")

    utcPreStart = datetime.strptime(goatData["preStartTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
    utcPreStart = utcPreStart.replace(tzinfo=from_zone)
    preStartDt = utcPreStart.astimezone(to_zone)
    preStartTime = preStartDt.strftime("%m/%d %I:%M:%S %p %Z")

    utcNextPreStart = datetime.strptime(goatData["nextPreStartTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
    utcNextPreStart = utcNextPreStart.replace(tzinfo=from_zone)
    nextPreStartDt = utcNextPreStart.astimezone(to_zone)
    nextPreStartTime = nextPreStartDt.strftime("%m/%d %I:%M:%S %p %Z")
    if goatData["product"]["name"] == productName:
        print("({}) No new product detected. No action taken (Check OOS? = {})".format(logTime, lookForSoldOut))
    else:
        print("({}) New product detected. Sending webhooks (Check OOS? = {})".format(logTime, lookForSoldOut))
        productName = goatData["product"]["name"]
        lookForSoldOut = True
        for webhook in webhookUrls:
            embed = Webhook(webhook, color=123123)
            embed.set_author(name='Goat Surprise Monitor', icon="https://i.imgur.com/GIOTCug.jpg")
            embed.set_thumbnail(url=goatData["product"]["pictureUrl"])
            embed.set_title(title=goatData["product"]["name"], url=productUrl)
            embed.set_desc("The next drop usually occurs **10 minutes** after `Next Pre Start Time`.\nNext product is announced at `Next Pre Start Time`.\nClick [this]({}) to access product from website, (**Disclaimer:** Will not work on apparel).".format(productUrl))
            embed.add_field(name='Price', value="`${:,.2f}`".format(goatData["product"]["priceCents"] / 100))
            embed.add_field(name='Pre Start Time', value="`{}`".format(preStartTime))
            embed.add_field(name='Start Time', value="`{}`".format(startTime))
            embed.add_field(name='End Time', value="`{}`".format(endTime))
            embed.add_field(name='Next Pre Start Time', value="`{}`".format(nextPreStartTime))
            embed.post()
    if lookForSoldOut == True:
        if "isSoldOut" in goatData:
            if goatData["isSoldOut"] == True:
                try:
                    print("({}) Product sold out. Sending webhooks. (Check OOS? = {})".format(logTime, lookForSoldOut))
                    lookForSoldOut = False
                    for webhook in webhookUrls:
                        embed1 = Webhook(webhook, color=123123)
                        embed1.set_author(name='Goat Surprise Monitor', icon="https://i.imgur.com/GIOTCug.jpg")
                        embed1.set_thumbnail(url=goatData["product"]["pictureUrl"])
                        embed1.set_title(title=goatData["product"]["name"], url=productUrl)
                        embed1.set_desc("The next drop usually occurs **10 minutes** after `Next Pre Start Time`.\nNext product is announced at `Next Pre Start Time`.\nClick [this]({}) to access product from website, (**Disclaimer:** Will not work on apparel).".format(productUrl))
                        embed1.add_field(name='Sold Out', value="`{}`".format(goatData["isSoldOut"]))
                        embed1.add_field(name='Next Pre Start Time', value="`{}`".format(nextPreStartTime))
                        embed1.post()
                except KeyError:
                    pass
    time.sleep(5)

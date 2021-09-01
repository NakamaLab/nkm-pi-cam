#!/usr/bin/python

# como correr como servicio https://www.raspberrypi.org/forums/viewtopic.php?t=197513
# https: // medium.com/@matmoody/how-to-connect-the-twitter-streaming-api-and-slack-with-python-for-instant-notifications-bdd6c375e0a0

from __future__ import absolute_import, print_function
import picamera
import datetime
import shutil
import tweepy
import logging
from time import sleep
import paho.mqtt.client as mqtt
import json
from os import system
from systemd.journal import JournaldLogHandler

with open('config.json') as config_file:
    config = json.load(config_file)

# get an instance of the logger object this module will use
logger = logging.getLogger(__name__)

# instantiate the JournaldLogHandler to hook into systemd
journald_handler = JournaldLogHandler()

# set a formatter to include the level name
journald_handler.setFormatter(logging.Formatter(
    '[%(levelname)s] %(message)s'
))

# add the journald handler to the current logger
logger.addHandler(journald_handler)

# optionally set the logging level
logger.setLevel(logging.DEBUG)

photo_path = '/home/pi/cam/data/latest.jpg'
video_path = '/home/pi/cam/data/latest_video'

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
consumer_key = config['tweepy']['consumer_key']
consumer_secret = config['tweepy']['consumer_secret']

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located
# under "Your access token")
access_token = config['tweepy']['access_token']
access_token_secret = config['tweepy']['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# If the authentication was successful, you should
# see the name of the account print out
print(api.me().name)


# Captures an image and copies to latest.jpg. Needs to be passed a datetime
# object for the timestamped image, t.
def capture_image(t):
    ts = t.strftime('%Y-%m-%d-%H-%M')
    with picamera.PiCamera() as cam:
        cam.resolution = (1024, 768)
        cam.annotate_background = picamera.Color('black')
        cam.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Camera warm-up time
        cam.start_preview()
        sleep(1)
        # cam.hflip = True
        # cam.vflip = True
        cam.capture(photo_path, quality=50)
    return


def tweet_video(api):
    try:
        t = datetime.datetime.now()
        status = 'Video auto-tweet from Pi: ' + t.strftime('%Y/%m/%d %H:%M:%S')
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.start_preview()
            for i in range(15):
                camera.annotate_background = picamera.Color('black')
                camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                camera.capture(
                    video_path + '{0:04d}.jpg'.format(i), quality=20)
                sleep(2)

        # genera el gif animado con ImageMagic
        system('convert -delay 150 -loop 0 ' +
               video_path + '*.jpg ' + video_path + '.gif')
        api.update_with_media(video_path+'.gif', status=status)
        logger.info(status)
    except Exception as e:
        logger.fatal(e, exc_info=True)


def tweet_image(api):
    try:
        t = datetime.datetime.now()
        capture_image(t)
        status = 'Photo auto-tweet from Pi: ' + t.strftime('%Y/%m/%d %H:%M:%S')
        # If the application settings are set for "Read and Write" then
        # this line should tweet out the message to your account's
        # timeline. The "Read and Write" setting is on https://dev.twitter.com/apps
        api.update_with_media(photo_path, status=status)
        logger.info(status)
    except Exception as e:
        logger.fatal(e, exc_info=True)

# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(config['mqtt']['topic'])

# The callback for when a PUBLISH message is received from the server.


def on_message(client, userdata, msg):
    global api
    payload = str(msg.payload)
    if 'video' in payload:
        tweet_video(api)
    else:
        tweet_image(api)


if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config['mqtt']['server'], config['mqtt']['port'], 60)
    client.username_pw_set(config['mqtt']['user'], config['mqtt']['pass'])
    client.loop_start()

    try:
        while True:
            logger.info("Alive...")
            sleep(600)
    except KeyboardInterrupt as e:
        logger.info("Stopping...")

    client.loop_stop(force=True)

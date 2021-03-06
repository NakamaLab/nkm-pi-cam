# Introduction

Python program that listens to a MQTT topic and publish a still image or an animated gif to twitter.

**WORK IN PROGRESS**

# Prerequisites

- A raspberry pi / zero with raspbian lite
- Python 3 (allready installed on raspbian lite)
- Pip 3 to install requirements
  - picamera
  - tweepy
  - systemd
  - paho-mqtt
- A Tweeter account: dont use your personal account, create a new private account, ant then follow this new account from your personal account (activate notifications , every time the programs publish a tweet you'll get notified)
- A secure MQTT server on internet (dont use a public one). Some free options io.adafruit.com / cloudamqp.com

```bash
$ sudo apt-get update
$ sudo apt-get -y install python3-pip python3-picamera git imagemagick
$ cd ~
$ git clone https://github.com/NakamaLab/nkm-pi-cam ./cam
$ cd cam
$ pip3 install -r requirements.txt
```

# Configuration

Create a `config.json` file with the following data

```json
{
  "tweepy": {
    "consumer_key": "application's Details https://dev.twitter.com/apps (under 'OAuth settings')",
    "consumer_secret": "application's Details https://dev.twitter.com/apps (under 'OAuth settings')",
    "access_token": "application's Details https://dev.twitter.com/apps (under 'Your access token')",
    "access_token_secret": "application's Details https://dev.twitter.com/apps (under 'Your access token')"
  },
  "mqtt": {
    "server": "a.server.cloudamqp.com",
    "port": 1883,
    "user": "username",
    "pass": "a_passwrod",
    "topic": "home/nkm-pi-cam/command"
  }
}
```

# Running as a Service

```bash
$ sudo cp ~/cam/nkm-pi-cam.service /etc/systemd/system
$ systemctl enable nkm-pi-cam
$ systemctl start nkm-pi-cam
# view logs
$ journalctl -u nkm-pi-cam
```

Uninstall

```bash
$ systemctl stop nkm-pi-cam
$ systemctl disable nkm-pi-cam
```

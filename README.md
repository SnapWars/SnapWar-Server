# SnapWar Server

Simple Python server to serve SnapWar mobile app.

## First-time Setup

1. Navigate to https://console.firebase.google.com/u/0/project/snapwar-42955/overview,
go to Project Settings > Service accounts > Select 'Python' as Admin SDK configuration snippet,
then click `Generate new private key` and save the file into this same directory with name `key.json`

## Local Development

1. To start server, run `docker-compose up`

2. Find your computer's IP address, for MacOS it is located in System Preferences -> Network

3. Set the root URL to `{IP_ADDRESS}:8080` in mobile client to communicate with server

@echo off
docker build -t devilconnection-patcher-linux .
docker run --rm -v %cd%/dist:/output devilconnection-patcher-linux
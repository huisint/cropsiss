# Copyright (c) 2022 Shuhei Nitta. All rights reserved.

# Command line arguments
PLATFORM=$1

# Constants
VERSION="101.0.4951.64-0ubuntu0.18.04.1"
ARCH=`echo $PLATFORM | cut -d '/' -f 2`
URL_BASE="https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files"

# Install fonts
apt-get update
apt-get install -y wget fonts-ipafont fonts-ipaexfont
# Download chromium
wget ${URL_BASE}/chromium-codecs-ffmpeg_${VERSION}_${ARCH}.deb
wget ${URL_BASE}/chromium-codecs-ffmpeg-extra_${VERSION}_${ARCH}.deb
wget ${URL_BASE}/chromium-browser_${VERSION}_${ARCH}.deb
wget ${URL_BASE}/chromium-chromedriver_${VERSION}_${ARCH}.deb
# Install chromium
apt-get install -y ./chromium-codecs-ffmpeg_${VERSION}_${ARCH}.deb
apt-get install -y ./chromium-codecs-ffmpeg-extra_${VERSION}_${ARCH}.deb
apt-get install -y ./chromium-browser_${VERSION}_${ARCH}.deb
apt-get install -y ./chromium-chromedriver_${VERSION}_${ARCH}.deb
rm -rf /var/lib/apt/lists/*
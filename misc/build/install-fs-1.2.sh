#!/bin/bash

###############################################################################
# This should be all you need to INSTALL FreeSWITCH v1.2.x on Ubuntu 12.04 LTS.
# This installs a basic (or vanilla) FreeSWITCH setup for you. Of course you
# can only do that once you've built your debs. Find the build script and run
# that first (but on a different box).
# Also, let me know if it needs updated/fixed: Gabriel Gunderson gabe@gundy.org
###############################################################################

sudo apt-get update
sudo apt-get -y install flac libodbc1 unixodbc libjpeg62 sox

sudo dpkg -i \
    freeswitch-conf-vanilla_1.2.stable*.deb \
    freeswitch-meta-vanilla_1.2.stable*.deb \
    freeswitch-mod-amr_1.2.stable*.deb \
    freeswitch-mod-cdr-csv_1.2.stable*.deb \
    freeswitch-mod-cluechoo_1.2.stable*.deb \
    freeswitch-mod-commands_1.2.stable*.deb \
    freeswitch-mod-conference_1.2.stable*.deb \
    freeswitch-mod-console_1.2.stable*.deb \
    freeswitch-mod-db_1.2.stable*.deb \
    freeswitch-mod-dialplan-asterisk_1.2.stable*.deb \
    freeswitch-mod-dialplan-xml_1.2.stable*.deb \
    freeswitch-mod-dptools_1.2.stable*.deb \
    freeswitch-mod-enum_1.2.stable*.deb \
    freeswitch-mod-esf_1.2.stable*.deb \
    freeswitch-mod-event-socket_1.2.stable*.deb \
    freeswitch-mod-expr_1.2.stable*.deb \
    freeswitch-mod-fifo_1.2.stable*.deb \
    freeswitch-mod-fsv_1.2.stable*.deb \
    freeswitch-mod-g723-1_1.2.stable*.deb \
    freeswitch-mod-g729_1.2.stable*.deb \
    freeswitch-mod-h26x_1.2.stable*.deb \
    freeswitch-mod-hash_1.2.stable*.deb \
    freeswitch-mod-httapi_1.2.stable*.deb \
    freeswitch-mod-local-stream_1.2.stable*.deb \
    freeswitch-mod-logfile_1.2.stable*.deb \
    freeswitch-mod-loopback_1.2.stable*.deb \
    freeswitch-mod-lua_1.2.stable*.deb \
    freeswitch-mod-native-file_1.2.stable*.deb \
    freeswitch-mod-say-en_1.2.stable*.deb \
    freeswitch-mod-sndfile_1.2.stable*.deb \
    freeswitch-mod-sofia_1.2.stable*.deb \
    freeswitch-mod-spandsp_1.2.stable*.deb \
    freeswitch-mod-speex_1.2.stable*.deb \
    freeswitch-mod-tone-stream_1.2.stable*.deb \
    freeswitch-mod-valet-parking_1.2.stable*.deb \
    freeswitch-mod-voicemail_1.2.stable*.deb \
    freeswitch-music-default*.deb \
    freeswitch-sounds-en-us-callie*.deb \
    freeswitch-sysvinit_1.2.stable*.deb \
    freeswitch_1.2.stable*.deb \
    libfreeswitch1_1.2.stable*.deb

echo "**************************************************************************"
echo "There are a few additional things that you'll need to do to get started..."
echo "sudo cp -a /usr/share/freeswitch/conf/vanilla /etc/freeswitch"
echo "**************************************************************************"


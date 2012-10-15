#!/bin/bash

###############################################################################
# This should be all you need to build FreeSWITCH v1.2.x on Ubuntu 12.04 LTS.
# The process has been radically changed (for the better) and while there is
# *some* documentation out there, a bash-and-forget script was not to be found.
# The key parts of this script are from the (FS Source)/debialREADME.source,
# where Travis Cross (tc) spells it out. Thanks Travis!
# Also, let me know if it needs updated/fixed: Gabriel Gunderson gabe@gundy.org
###############################################################################


###############################################################################
# Step one - Build the standard debs for the core and all its modules.
###############################################################################

# You have a chance to set some vars before we start.
GIT_USER="Some User"
GIT_EMAIL="bounces@example.com"
DISTRO="precise"
VERSION="1.2.stable"
BUILD_NUMBER="1"
FINAL_DIR="FreeSWITCH-DEBs"

# Variables that we don't manually set.
VER="$(echo "${VERSION}" | sed -e 's/-/~/g')~n$(date +%Y%m%dT%H%M%SZ)-1~${DISTRO}+${BUILD_NUMBER}"

if [ "$(id -u)" == "0" ]; then
    echo "This script should NOT be run as root." 2>&1
    echo "But, you will have to have sudo access." 2>&1
    exit 1
fi

# Make a new home for our debs.
mkdir -p ${FINAL_DIR}/debug

# Simple function to reset git.
reset_git(){
    git clean -fdx && git reset --hard
}

# Before we do anything, let's get the box updated:
sudo apt-get update
sudo apt-get dist-upgrade -y

# We'll need install git before we can move ahead.
sudo apt-get install git -y

# And now, grab the code.
git clone -b v${VERSION} git://git.freeswitch.org/freeswitch.git

# Install all the need deps (ends up installing 300+ packages).
sudo apt-get install -y \
autoconf \
bison \
debhelper \
default-jdk \
devscripts \
doxygen \
dpkg-dev \
erlang-dev \
fakeroot \
flac \
gcj-jdk \
ladspa-sdk \
libasound2-dev \
libdb-dev \
libexpat1-dev \
libflac-dev \
libgdbm-dev \
libjpeg62-dev \
libncurses5-dev \
libogg-dev \
libperl-dev \
libpq-dev \
libsnmp-dev \
libtool \
libvlc-dev \
libvorbis-dev \
libx11-dev \
libyaml-dev \
python-dev \
sox \
unixodbc-dev \
uuid-dev

# Move into the repo.
cd freeswitch

# Clean up the repo in case there's junk laying around.
reset_git

# Set our specific build version.
./build/set-fs-version.sh ${VER}

git config --global user.name "${GIT_USER}"
git config --global user.email ${GIT_EMAIL}

# Commit changes to the debian configure file.
git add configure.in && git commit -m "Bump to custom version, ${VER}."

# Run the custom FreeSWITCH bootstrap file.
(cd debian && ./bootstrap.sh -c ${DISTRO})

# Update the debian changelog.
dch -b -m -v "${VER}" --force-distribution -D "UNRELEASED" "Custom build."

# And finally, build some debs (binary, unsigned). 
dpkg-buildpackage -b -us -uc -Zxz -z9

# Reset the index and working tree (clean up after our selves).
reset_git

# Get out of the git repo.
cd -


###############################################################################
# Step two - Build the audio debs (they're handeled differently than code).
###############################################################################

SOUNDS="freeswitch-sounds-en-us-callie freeswitch-music-default"

# Build process for each sound.
for SOUND in ${SOUNDS}; do
    git clone https://github.com/traviscross/freeswitch-sounds.git
    cd freeswitch-sounds
    bash debian/bootstrap.sh -p ${SOUND}
    ./debian/rules get-orig-source
    tar -xv --strip-components=1 -f *_*.orig.tar.xz && mv *_*.orig.tar.xz ../
    dpkg-buildpackage -uc -us -Zxz -z9
    cd -
    rm -fR freeswitch-sounds
done


###############################################################################
# That's it, we're ready to rock.
###############################################################################

# Move the standard .debs into one place.
mv *-dbg_*.deb ${FINAL_DIR}/debug/
mv *.deb ${FINAL_DIR}

echo "You have built `find -name *.deb | wc -l` FreeSWITCH debs."
echo "Find them in the ${FINAL_DIR} directory."

#!/bin/bash

# We should start by updating packages lists.
sudo apt-get update

# We need git to check out the code.
sudo apt-get -y install git-core

# Check out the code at the latest branch.
git clone git://git.freeswitch.org/freeswitch.git freeswitch_git

# Now we need the basic tools we'll need to build debs.
sudo apt-get -y install \
	devscripts \
	build-essential \
	fakeroot

# We could have installed this before, but this way we're clear about what
# these packages actually depend on.
sudo apt-get -y install \
	autoconf \
	automake \
	bison \
	debhelper \
	libasound2-dev \
	libcurl4-openssl-dev \
	libdb-dev \
	libgdbm-dev \
	libgnutls-dev \
	libogg-dev \
	libperl-dev \
	libssl-dev \
	libtiff4-dev \
	libtool \
	libvorbis-dev \
	libx11-dev \
	ncurses-dev \
	python-dev \
	unixodbc-dev \
	uuid-dev

# Change directories to the newly checked out source code.
cd freeswitch_git

# Now, we actually do the work of building... this might take a few mins.
debuild -i -us -uc -b

# Go back to the parent directory.
cd ..

# Let's make a nice place to hold all of these shiny new .debs :)
mkdir freeswitch_debs

# And now move them into their new home.
mv freeswitch[_-]*.deb freeswitch_debs/

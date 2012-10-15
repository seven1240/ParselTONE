#!/bin/bash

# We should start by updating packages lists.
sudo apt-get update

# We need subversion to check out the code.
sudo apt-get -y install subversion

# Check out the code at the latest branch.
svn co https://opensips.svn.sourceforge.net/svnroot/opensips/branches/1.7 \
	opensips-1.7

# Now we need the basic tools we'll need to build debs.
sudo apt-get -y install \
	build-essential \
	debhelper \
	devscripts \
	fakeroot

# Change directories to the newly checked out source code.
cd opensips-1.7/

# The build wants the 'debian' dir here in the root of the source.
ln -s packaging/debian debian

# We could have installed this before, but this way we're clear about what
# these packages actually depend on.
sudo apt-get -y install \
	bison \
	dpatch \
	flex \
	libconfuse-dev \
	libcurl4-gnutls-dev \
	libdb-dev \
	libexpat1-dev \
	libgeoip-dev \
	libjson0-dev \
	libldap2-dev \
	libmemcached-dev \
	libmysqlclient15-dev \
	libpcre3-dev \
	libperl-dev \
	libpq-dev \
	libradiusclient-ng-dev \
	libsnmp-dev \
	libxml2-dev \
	libxmlrpc-c3-dev \
	unixodbc-dev \
	xsltproc \
	zlib1g-dev

# Now, we actually do the work of building... this might take a few mins.
debuild -i -us -uc -b

# Go back to the parent directory.
cd ..

# Let's make a nice place to hold all of these shiny new .debs :)
mkdir opensips_debs

# And now move them into their new home.
mv opensips[_-]*.deb opensips_debs/

# If you're happy with the build, you can clean this up (you might want to review them first).
rm opensips_1.7.0-1_amd64.build opensips_1.7.0-1_amd64.changes

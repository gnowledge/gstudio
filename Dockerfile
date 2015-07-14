from ubuntu:14.04

maintainer nagarjun@gnowledge.org

RUN useradd -ms /bin/bash docker



run apt-get update
run apt-get install -y build-essential git python python-setuptools python-dev rcs emacs24 libjpeg-dev memcached libevent-dev libfreetype6-dev zlib1g-dev nginx supervisor curl g++ make
run easy_install pip

# install uwsgi now because it takes a little while
run pip install uwsgi nodeenv

# install nginx
run apt-get install -y python-software-properties
run apt-get install -y software-properties-common python-software-properties
run add-apt-repository -y ppa:nginx/stable
run apt-get install -y sqlite3

# for ffmpeg 
run add-apt-repository ppa:mc3man/trusty-media
run apt-get update
run apt-get install -y ffmpeg gstreamer0.10-ffmpeg

# for nodejs
run add-apt-repository ppa:chris-lea/node.js
run apt-get update
run apt-get install -y  nodejs  
run npm install -g bower

# creating user for bower
# run adduser --disabled-password --gecos '' buser
# run adduser buser sudo
# run echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
# run chown buser: /root/.config/configstore/bower-github.yml

# RUN useradd -ms /bin/bash docker

# install our code
add . /home/docker/code/
run mv /home/docker/code/bower_components /home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/static/ndf/

# RUN chown -R docker /home/docker/

# ENV HOME /home/docker
# USER docker


# setup all the configfiles
run echo "daemon off;" >> /etc/nginx/nginx.conf
run rm /etc/nginx/sites-enabled/default
run ln -s /home/docker/code/nginx-app.conf /etc/nginx/sites-enabled/
run ln -s /home/docker/code/supervisor-app.conf /etc/supervisor/conf.d/



# run pip install
run pip install -r /home/docker/code/gstudio/requirements.txt


# mongodb installation

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r mongodb && useradd -r -g mongodb mongodb

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ca-certificates \
		numactl
#	&& rm -rf /var/lib/apt/lists/*

# grab gosu for easy step-down from root
RUN gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4
RUN curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.2/gosu-$(dpkg --print-architecture)" \
	&& curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.2/gosu-$(dpkg --print-architecture).asc" \
	&& gpg --verify /usr/local/bin/gosu.asc \
	&& rm /usr/local/bin/gosu.asc \
	&& chmod +x /usr/local/bin/gosu

# gpg: key 7F0CEB10: public key "Richard Kreuter <richard@10gen.com>" imported
RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys 492EAFE8CD016A07919F1D2B9ECBEC467F0CEB10


RUN echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.1 multiverse" > /etc/apt/sources.list.d/mongodb-org.list




RUN set -x \
	&& apt-get update \
	&& apt-get install -y \
		mongodb-org-unstable \
		mongodb-org-unstable-server \
		mongodb-org-unstable-shell \
		mongodb-org-unstable-mongos \
		mongodb-org-unstable-tools \
#	&& rm -rf /var/lib/apt/lists/* \
	&& rm -rf /var/lib/mongodb \
	&& mv /etc/mongod.conf /etc/mongod.conf.orig

RUN mkdir -p /data/db && chown -R mongodb:mongodb /data/db
VOLUME /data/db

# COPY mongodb.sh /mongodb.sh
# run chmod +x /mongodb.sh
# ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 27017
expose 80

# nltk installation and building search base

run pip install -U pyyaml nltk
run /home/docker/code/nltk-initialization.py

CMD ["mongod"]

# run service mongod start
# edit the following file to change the default superuser password 
# this also does syncdb and filldb 
run mkdir /home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/management/commands/schema_files
run /home/docker/code/initialize.sh

# change this line for your timezone
run ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime

cmd ["supervisord", "-n"]

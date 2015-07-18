# gstudio-docker
Docker file for gstudio
=======================

To build the docker image, we need to clone the project in your docker host, and run the script build-docker.sh. This script clones the gstudio code and builds the image. After clining the gstudio-docker, download and install the static javascript depedencies from [[http://gnowledge.org/~nagarjun/bower_components.tar.gz]]. unzip the contents of this file in the project directory before starting the buuild-docker.sh script.

The image uses Ubuntu 14.04, django, nginx, mongodb, and several code dependent python libraries and OS level libraries.  The image builds to about 1.6GB.  

Under development
-----------------

- autostart of mongod issue to be resolved
- schema files to be updated for course builder and course player
- single point data directory for all data (mongo, sqlite, static files, rcs files, mail queue, etc.)
- after successful completion of the above tasks the docker project to be published in dockerhub.
- security enhancements
  - run all services as non-root user
  - expose only port 80
  - gpg keys installation script for school servers joining auto-sync program.

Building the Image
------------------

Build the image by running "build-docker.sh" script from the project directory after cloning the project files. If you are re-building the image, delete the 'gstudio' directory to get the fresh updates from gstudio project. 


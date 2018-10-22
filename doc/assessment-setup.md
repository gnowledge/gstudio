# Setting `oac`, `oat` on any server:

1. **qbank**
- 1.1. `git clone https://github.com/gnowledge/qbank-lite.git` at `manage.py` level.
- 1.2. `git checkout clixserver.tiss.edu`
- 1.3. Make appropriate changes in `main.py` file w.r.t domain name. 
- 1.4 Make sure docker container has port `8080` exposed.


2. **Data**
- 2.1. mongodb - dump required collections (from data in source server) and restore (destination staging)
    + 2.2.2. Restore: `mongorestore --drop mongodump`
- 2.2. Files: Copy from `clix` folder of installer.
    + 2.2.1. Copy: `cp -rv CLIx/datastore/AssetContent/* /home/docker/code/gstudio/gnowsys-ndf/qbank-lite/webapps/CLIx/datastore/repository/AssetContent/`


3. **OpenAssessmentsClient**
- 3.1. `git clone https://github.com/gnowledge/OpenAssessmentsClient.git` (at anywhere).
- 3.2. `cd OpenAssessmentsClient` then `git checkout clixserver.tiss.edu`
- 3.3. Make sure you have updated node version installed (on system where you are doing following steps).
- 3.4. Make appropriate changes in: https://github.com/gnowledge/OpenAssessmentsClient/blob/master/client/html/layouts/partials/_head.html w.r.t domain name.
- 3.5. Make sure you have appropriate entries in `nginx.conf` file for `/softwares/` and `oac`, `oat`.
- 3.6. Run: https://github.com/gnowledge/OpenAssessmentsClient/blob/master/yarn-build.sh
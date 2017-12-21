Dump Restore
============

DEPRICATED AS ON 12 APRIL 2017 - katkamrachana **Merging of 2 different
instance's data.**

How to Restore ?

-  Suppose we have backup of 2 schools/servers say S1 ad S2.
-  S1 /data having:

   -  db
   -  rcs-repo
   -  media

-  S2 /data having:

   -  db
   -  rcs-repo
   -  media

**Step 1**: On a clean /data, copy S1's /data.

**Step 2**: Run "python manage.py data\ :sub:`dump`" This will create
'gstudio:sub:`datarestore`' under /data that will contain the RCS files.

**Step 3**: Take dump of Benchmarks collection. (Since we do not have
RCS of this collection) Run "mongodump --db <db:sub:`name`> --collection
Benchmarks *data/gstudio\ :sub:`datarestore`/Benchmarks:sub:`dump`*"
This will create a Benchmarks.bson file.

**Step 4**: On a clean /data, copy S2's /data.

**Step 5**: Go to shell: python manage.py shell

**Step 6**: execfile('../doc/deployer/restore\ :sub:`dump`.py') This
file takes rcs dump created in step 2. Paths defined: nodes\ :sub:`path`
= '/data/gstudio:sub:`datarestore`/data/rcs-repo/Nodes'
triples\ :sub:`path` =
'/data/gstudio:sub:`datarestore`/data/rcs-repo/Triples'
filehives\ :sub:`path` =
'/data/gstudio:sub:`datarestore`/data/rcs-repo/Filehives' Modify these
paths, if you have moved the Step 2 output location.

**Step 7**: Restore Benchmarks collection dump of Step 3. Run:
mongorestore --db meta-mongodb --collection
/data/gstudio:sub:`datarestore`/Benchmarks:sub:`dump`/Benchmarks.bson

**Step 8**: Run fix\ :sub:`nodes`.py. This script resets data-type of
all the datetime related values from long to datetime object

**Note**: S1 and S2 should be updated with alpha branch (Filehive
implementation)
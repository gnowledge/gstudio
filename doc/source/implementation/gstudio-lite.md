# gStudio-Lite
> Elastic Search & RCS implementation of gStudio


### Update following files & modules:

- **`requirements.txt`:**
    + Strip down to only necessary ones.
    + Are we going with oac/oat? Needs to take decision to strikeout qbank requirements accordingly.

- **Update `INSTALL.txt`**

- **SQL User DB**
    + Are we continuing with sql db for user?
    + If yes, then are we going with `sqlite` of `postgreSQL` ?

- **`fab` commands**

- **Development possibilities?**
    + If yes, then we can continue with development requirements else we can remove them.

- **Code to update in following modules**
    + [benchmarker](https://github.com/gnowledge/gstudio/tree/master/gnowsys-ndf/gnowsys_ndf/benchmarker)
        + We can remove benchmarker or do changes.
    + [settings.py](https://github.com/gnowledge/gstudio/blob/master/gnowsys-ndf/gnowsys_ndf/settings.py) and `local_settings.py`
    + [ndf](https://github.com/gnowledge/gstudio/tree/master/gnowsys-ndf/gnowsys_ndf/ndf)
        + [commands](https://github.com/gnowledge/gstudio/tree/master/gnowsys-ndf/gnowsys_ndf/ndf/management/commands)
        + [models](https://github.com/gnowledge/gstudio/tree/master/gnowsys-ndf/gnowsys_ndf/ndf/models):
            * Override following *collection instances* with equivalent *elastic search (ES)* implementation:
                - `node_collection`
                - `triple_collection` 
                - `benchmark_collection` 
                - `filehive_collection` 
                - `buddy_collection` 
                - `counter_collection` 
            * Override following for ES and call existing for mongo:
                - `one()`
                - `find()`
                - `find_one()`
                - `update()`
                - `<collection instances>.collection.<classname>()`  # *to create new instance*
            * These overriding can be taken to separate file next to models or at root level.
            * While overriding take care that we are supporting all mongo queries, operators and it has equivalent implementation in ES.
        + Check code in following:
            * [templatetags](https://github.com/gnowledge/gstudio/tree/master/gnowsys-ndf/gnowsys_ndf/ndf/templatetags) 
            * [views](https://github.com/gnowledge/gstudio/tree/master/gnowsys-ndf/gnowsys_ndf/ndf/views)


### To Do
- Script to inject existing data objects to ES container
- Update `save()` in models to inject new and updated object to ES container
- Implement `update` method to:
    + Call default mongo `update()`
    + Implement custom for ES
- ...
- ...


### Challenges:
- ...
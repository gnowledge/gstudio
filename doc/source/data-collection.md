# Data Collection [Complete]

All the CLIx schools are running either of the platforms:
    [1]. gStudio
    [2]. unplatform, in schools where servers are not available, etc.

**GENERIC STRUCTURE**:

The directory/folder structure of collected data is maintained as `LEVEL 0/.../LEVEL N`
Read below for description of LEVELs.

```
Year (YYYY)                                             [ LEVEL 0 ]
    State (State Code)                                  [ LEVEL 1 ]
        - School (School Code + Server ID)              [ LEVEL 2 ]
            - gstudio (Clix Platform)                   [ LEVEL 3 ]
                - db                                    [ LEVEL 4 ]
                - media                                 [ LEVEL 4 ]
                - rcs-repo                              [ LEVEL 4 ]
                - postgres-dump                         [ LEVEL 4 ]
                    - pg_dump_all.sql                   [ LEVEL 5 ]
                - system-heartbeat                      [ LEVEL 4 ]
                - gstudio-exported-users-analytics-csvs [ LEVEL 4 ]
                - gstudio_tools_logs                    [ LEVEL 4 ]
                - gstudio-logs                          [ LEVEL 4 ]
                - local_settings.py                     [ LEVEL 4 ]
                - server_settings.py                    [ LEVEL 4 ]
                - git-commit.log                        [ LEVEL 4 ]
                - assessment-media                      [ LEVEL 4 ]
                    - repository                        [ LEVEL 5 ]
                    - studentResponseFiles              [ LEVEL 5 ]
                - nginx-logs                            [ LEVEL 4 ]
            - unplatform (Optional)                     [ LEVEL 3 ]
```

**[ LEVEL 0 ] : Year (YYYY)**
- Year when data is collected.
- Example: 
    - 2016
    - 2017
    - 2018

**[ LEVEL 1 ] : State (State Code)**
- Small case state code, which we have used in our school instances.
- Possible values: 
    - Mizoram      : **mz**
    - Rajasthan    : **rj**
    - Chhattisgarh : **ct**
    - Telangana    : **tg**

**[ LEVEL 2 ] : School (School Code + Server ID)**
- It's combination of "school code" and "server id"
- i.e: `<school code>-<server id>`
- Example: 2031001-mz1

> *NOTE:
In order to address scenario where the schools might run both gStudio and unplatform in parallel, 
we have a provision to collect data from the said platforms and both may reside at [LEVEL 3]. To maintain this structure as generic, we are naming `clixserver` as `gstudio`.*

**[ LEVEL 3 ] : gstudio**
- A CLIx Platform, clixserver.

**[ LEVEL 4 ] : data**
- gstudio Folder will have following [LEVEL 4] items:
    - `db`: mongoDB data *(gStudio + qbank)*.
    - `media`: Files uploaded on clixserver *(gStudio)*.
    - `rcs-repo`: rcs, versioned json files *(gStudio)*.
    - `postgres-dump`: Postgres DB dump folder containing file `pg_dump_all.sql`. This is dump of user data.
    - `system-heartbeat`: Contains log of following:
        - Server Id
        - School Id
        - School Name
        - Internal IP Address
        - RAM usage details (`free -h`)
        - HDD usage details (`df -h`)
        - `uptime`
        - Current Processes (`ps aux`)
    - `gstudio-exported-users-analytics-csvs`: Folder, contains students unitwise quantitative data in CSV form.
    - `gstudio_tools_logs`: Tools (which supports data logging and configured gstudio end points) data in `json` format will be stored in this folder.
    - `gstudio-logs`: Folder containing gstudio level general logs for scripts and updates.
    - `local_settings.py`: Copy of file in deployed instance *(gStudio)*.
    - `server_settings.py`: Copy of file in deployed instance *(gStudio)*.
    - `git-commit.log`: Snapshot of git records at time of backup. It will have output of following git commands  *(gStudio + qbank)*:
        - `git status`
        - `git diff`
        - `git log -5`
        - `git branch`
    - `assessment-media`: Assessment files and user uploaded files in assessments. This folder will have following [LEVEL 5] directories *(qbank)*
        - `repository`: Files/Media used in assessments.
        - `studentResponseFiles`: User uploaded files in assessments e.g: recorded-audio, images etc. 
    - `nginx-logs`: Contains logs produced by nginx.


**EXAMPLE STRUCTURE**:
```
Example-data-collection-dir-str/
├── 2016
└── 2017
    ├── ct
    │   └── 01011011-ct11
    │       ├── gstudio
    │       │   ├── db
    │       │   ├── media
    │       │   ├── rcs-repo
    │       │   ├── postgres-dump
    │       │   |    └── pg_dump_all.sql
    │       |   ├── gstudio-exported-users-analytics-csvs
    │       |   ├── gstudio_tools_logs
    │       |   ├── gstudio-logs
    │       |   ├── system-heartbeat
    │       │   ├── local_settings.py
    │       │   ├── server_settings.py
    │       │   ├── git-commit.log
    │       │   ├── nginx-logs
    │       │   └── assessment-media
    │       │       ├── repository
    │       │       └── studentResponseFiles
    │       └── unplatform
    └── mz
        └── 02031001-mz1
            ├── gstudio
            │   ├── db
            │   ├── media
            │   ├── rcs-repo
            │   ├── postgres-dump
            │   |    └── pg_dump_all.sql
            │   ├── gstudio-exported-users-analytics-csvs
            │   ├── gstudio_tools_logs
            │   ├── gstudio-logs
            │   ├── system-heartbeat
            │   ├── local_settings.py
            │   ├── server_settings.py
            │   ├── git-commit.log
            │   ├── nginx-logs
            │   └── assessment-media
            │       ├── repository
            │       └── studentResponseFiles
            └── unplatform
```


---

## Derived Data
Derived data is one which we can pull out from above complete data by running scripts on it.

### 1. Activity Timestamp [format: CSV]
1.1 For **Single User**:
- Script Name: `activity_timestamp`
- Prerequisite:
    - Get in docker (ref. Utility 1)
    - Reach at required gstudio location within docker (ref. Utility 2)
- [RUN]: `python manage.py activity_timestamp <username>`
- Example [RUN]: `python manage.py activity_timestamp green-apple-sp100`

1.2 For **all user's**:
- Script Name: `get_all_users_activity_timestamp_csvs.py`
- Prerequisite:
    - Get in docker (ref. Utility 1)
    - Reach at required gstudio location within docker (ref. Utility 2)
    - Get into project shell (ref. Utility 3)
- [RUN]: `execfile('../doc/deployer/get_all_users_activity_timestamp_csvs.py')`

### 2. Progress CSV's: [format: CSV]
- Script name: `export_users_analytics`
- Prerequisite:
    - Get in docker (ref. Utility 1)
    - Reach at required gstudio location within docker (ref. Utility 2)
- [RUN]: `python manage.py export_users_analytics`

### 3. Assessments data [format: DB data dumps]
- Script Name: `single_school_get_MIT_activity_data.py`
- Prerequisite:
    - Get in docker (ref. Utility 1)
    - Reach at required gstudio location within docker (ref. Utility 4)
- [RUN]: `python single_school_get_MIT_activity_data.py`

---

## Utility Commands:
### 1. Get into docker [RUN]: `docker exec -it gstudio bash`
### 2. Reach at required `gstudio` location within docker [RUN]: `cd /home/docker/code/gstudio/gnowsys-ndf`
### 3. Get into project shell [RUN]: `python manage.py shell`
### 4. Reach at required `qbank-gstudio-scripts` location within docker [RUN]: `cd qbank-gstudio-scripts/single_school_get_MIT_activity_data/`
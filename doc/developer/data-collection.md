All the CLIx schools are running either of the platforms:
    [1]. gStudio
    [2]. unplatform, in schools where servers are not available, etc.

### GENERIC STRUCTURE:

The directory/folder structure of collected data is maintained as LEVEL 0/.../LEVEL N
Read below for description of LEVELs.

```
Year (YYYY)                                         [ LEVEL 0 ]
    State (State Code)                              [ LEVEL 1 ]
        - School (School Code + Server ID)          [ LEVEL 2 ]
            - gstudio (Clix Platform)               [ LEVEL 3 ]
                - db                                [ LEVEL 4 ]
                - media                             [ LEVEL 4 ]
                - rcs-repo                          [ LEVEL 4 ]
                - pgdump-YYYYMMDD-HHMM.sql          [ LEVEL 4 ]
                - local_settings.py                 [ LEVEL 4 ]
                - server_settings.py                [ LEVEL 4 ]
                - git-commit.log                    [ LEVEL 4 ]
            - unplatform (Optional)                 [ LEVEL 3 ]
```

**[ LEVEL 0 ] : Year (YYYY)**
- Year when Data is collected.
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
- gstudio Folder will have following [LEVEL 4] items:
    - `db`: mongoDB data.
    - `media`: Files uploaded on clixserver.
    - `rcs-repo`: rcs, versioned json files.
    - `pgdump-YYYYMMDD-HHMM.sql`: Postgres DB dump with specified naming convention.
    - `local_settings.py`: Copy of file in deployed instance.
    - `server_settings.py`: Copy of file in deployed instance.
    - `git-commit.log`: Snapshot of git records at time of backup. It will have output of following git commands:
        - `git status`
        - `git diff`
        - `git log -5`
        - `git branch`


---

### EXAMPLE STRUCTURE:
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
    │       │   ├── pgdump-20170921-1305.sql
    │       │   ├── local_settings.py
    │       │   ├── server_settings.py
    │       │   ├── git-commit.log
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
            │   ├── pgdump-20170921-1305.sql
            │   ├── local_settings.py
            │   ├── server_settings.py
            │   ├── git-commit.log
            │   └── assessment-media
            │       ├── repository
            │       └── studentResponseFiles
            └── unplatform
```

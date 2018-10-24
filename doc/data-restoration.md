# Data Restoration

## Pre Requisites:
- Ready with Expected Data (ED) backup-folder.

## STEP - I] Replace `data` folder
- Stop running `gstudio` server
    - `docker stop gstudio`
- [Check]: If server is stopped or not.
    + `docker ps`
    + Above command should not show any entry of container - `gstudio`  
- From terminal, move to expected data path
    - `cd </path/where/data/is/mounted>`
- Rename existing data folder with existing school *server-id*.
    + e.g: `data` --> `data-tg32`
    + This step is optional to make provision of new backup-folder which will be renamed as `data`
    + *Note: This step will persist `N` nos of folders after period of time, check for your HDD space*
- Copy/Move ED folder here. Choose either of following
    + **Copy** (notice **`.`** at end): `rsync -avzPh <path/to/ED/backup-folder> .`
    + **Move** (notice **`.`** at end): `mv -v <path/to/ED/backup-folder> .`
- Rename copied/moved ED backup-folder to `data`:
    + **Rename**: `mv  -v  <name of ED backup-folder>  data`

## STEP - II] Import users/`sql` data

## STEP - III] Replace settings files

## Post Restoration Checkpoints:
1. ..
2. ..
3. ..

---

## Summary:
- 2 data steps(step - I & II) and 1 configuration/settings step(step - III)
# Data Restoration

## Pre Requisites:
- Ready with Expected Data (ED) backup-folder.

## STEP - I] Replace `data` folder
- Stop running `gstudio` server
    - `docker stop gstudio`
  ![1](https://user-images.githubusercontent.com/21193492/50424177-5965e280-0886-11e9-8afd-01397845b69f.png)
 

- [Check]: If server is stopped or not.
    + `docker ps`
  ![2](https://user-images.githubusercontent.com/21193492/50424271-9d0d1c00-0887-11e9-8e54-f7333c8dad25.png)

    + Above command should not show any entry of container - `gstudio`  
- From terminal, move to expected data path
    - `cd </path/where/data/is/mounted>`
  
  ![2a](https://user-images.githubusercontent.com/21193492/50424406-f9bd0680-0888-11e9-9737-9dd00140fb37.png)


- Rename existing data folder with existing school *server-id*.
    + e.g: `data` --> `data-mz1`
  
  ![3](https://user-images.githubusercontent.com/21193492/50424289-ae562880-0887-11e9-8bf8-af5b678fb644.png)

    + This step is optional to make provision of new backup-folder containing `mz-9` users which will be renamed as `data`
    + *Note: This step will persist `N` nos of folders after period of time, check for your HDD space*
- Copy/Move ED folder here. Choose either of following
    + **Copy** (notice **`.`** at end): `rsync -avzPh <path/to/ED/backup-folder> .`
    + **Move** (notice **`.`** at end): `mv -v <path/to/ED/backup-folder> .`
  
![4](https://user-images.githubusercontent.com/21193492/50424291-ae562880-0887-11e9-89c9-20a32a730ba6.png)
  
  **note**: Here Expected Data Backup-folder named as: `schooldata` 

- Rename copied/moved ED backup-folder to `data`:
    + **Rename**: `mv  -v  <name of ED backup-folder>  data`
  
![5](https://user-images.githubusercontent.com/21193492/50424293-ae562880-0887-11e9-8d18-bef03bb3440c.png)


- Start the  `gstudio` server:
    + `docker start gstudio`
  
![6](https://user-images.githubusercontent.com/21193492/50424296-aeeebf00-0887-11e9-855e-b090853c2048.png)

- Navigate to  `clixserver.tiss.edu` to check whether we can login by `mz-9`:
    + Since 'mz-9' users have not been restored into postgres database, the result in below snapshot displays the login by the previous user i.e.`mz-1`
  
![7](https://user-images.githubusercontent.com/21193492/50424298-aeeebf00-0887-11e9-96c9-5465accd54c0.png)
    
    + To display `mz-9` school information, we can check in `Workspaces` of `clixserver.tiss.edu` :
  
![8](https://user-images.githubusercontent.com/21193492/50424301-af875580-0887-11e9-9e08-6c1eb96ecc28.png)
    
    + To show the comments of the `mz-9` school server, it displays the error as specified below:
  
![9](https://user-images.githubusercontent.com/21193492/50424304-af875580-0887-11e9-93f8-fe6877b03e98.png)

  - **note** : It displays error since, mz-9 users are not restored into the postgres database which is explained in the further step.

## STEP - II] Import users/`sql` data
- The step II describes importing `mz-9` users into the postgres database and removing the previous `mz-1` users from postgres.
    + To remove the previous postgres database which consist of `mz-1` users, follow the steps in the given snapshot: 
  
![10](https://user-images.githubusercontent.com/21193492/50424306-af875580-0887-11e9-96b4-702afd20ac81.png)
  
  **note**: to come out of the postgres, press `Ctrl+d` twice.
    
    + Next step is to import the `mz-9` users into postgres. To do so, we need to find the latest postgres dump sql file named as **"pg_dump_all.sql"** which is found at following path: `/data/postgres-dump/pg_dump_all.sql`
  

![11](https://user-images.githubusercontent.com/21193492/50424393-f0339e80-0888-11e9-9519-6e8bef2d7ce7.png)

    + Restore the `mz-9` users into postgres database by following command:
  
![13](https://user-images.githubusercontent.com/21193492/50424395-f0cc3500-0888-11e9-8ea5-090befae3f97.png)

    + Result of Restoration: The following snapshot display that the `mz-9` users has been successfully restored:
  
![14](https://user-images.githubusercontent.com/21193492/50424397-f0cc3500-0888-11e9-9a31-3a50d2997f33.png)

    + To view the comments of the `mz-9` school server:
  
![15](https://user-images.githubusercontent.com/21193492/50424398-f164cb80-0888-11e9-90a3-bfe757677616.png)
  
  **note**: Earlier it had displayed the error since `mz-9` users were not restored at step I.


## STEP - III] Replace settings files
- To login with the `mz-9` user, we need to replace the configuration file i.e. `settings` file ( which includes both local_settings.py and server_settings.py):
  
![16](https://user-images.githubusercontent.com/21193492/50424399-f164cb80-0888-11e9-9cb2-38e3d6629d9c.png)


## Post Restoration Checkpoints:
1. ..
2. ..
3. ..

---

## Summary:
- 2 data steps(step - I & II) and 1 configuration/settings step(step - III)
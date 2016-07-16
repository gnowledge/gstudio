BigBlueButton for gstudio
====================
1.*Initialization*

* For setting up BBB server on a local machine refer [here](http://docs.bigbluebutton.org/install/install.html)

2.*After taking a pull*

* Register SALT and URL in `local_settings.py`

>**NOTE**: Get `SALT` and `URL` of BigBlueButton by using the command ``bbb-conf --secret``. Add these details in `local_settings.py` as  
`SALT = <salt obtained from above command>` 
`URL = <url obtained from above command>`
 
>For testing, use  
`SALT = '8cd8ef52e8e101574e400365b55e11a6'`
`URL = 'http://test-install.blindsidenetworks.com/bigbluebutton/'`

* Run the following scripts in order

> * python manage.py create_schema ATs.csv   
> * python manage.py create_schema STs_run2.csv  
> * echo "execfile('property_order_reset.py')" | python manage.py shell 

* Run the command `crontab -e` and add the line `0 0 * * * python /home/docker/code/gstudio/gnowsys-ndf/manage.py event_update_status` in the end and save the file.  
To check if the crontab is added successfully use the command `crontab -l` and check for the above added line.

# WebPOSHost


## Pre-requisites

See the requirements.txt for list of dependencies

## Running the application
To run the application use:

```
sudo gunicorn -w 2 -b 0.0.0.0:8080 webposhost:app  --name WEBPOSHOST --user=<username> -p webposhost.pid -D -c conf.py 
```

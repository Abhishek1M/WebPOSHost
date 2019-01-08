# WebPOSHost

<a href="https://snyk.io/test/github/Abhishek1M/WebPOSHost?targetFile=requirements.txt"><img src="https://snyk.io/test/github/Abhishek1M/WebPOSHost/badge.svg?targetFile=requirements.txt" alt="Known Vulnerabilities" data-canonical-src="https://snyk.io/test/github/Abhishek1M/WebPOSHost?targetFile=requirements.txt" style="max-width:100%;"></a>

[![Known Vulnerabilities](https://snyk.io/test/github/Abhishek1M/WebPOSHost/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/Abhishek1M/WebPOSHost?targetFile=requirements.txt)

## Pre-requisites

See the requirements.txt for list of dependencies

## Running the application
To run the application use:

```
sudo gunicorn -w 2 -b 0.0.0.0:8080 webposhost:app  --name WEBPOSHOST --user=<username> -p webposhost.pid -D -c conf.py 
```

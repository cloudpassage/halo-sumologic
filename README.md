# halo-sumologic

BETA

Installation instructions: https://help.sumologic.com/07Sumo-Logic-Apps/22Security_and_Threat_Detection/CloudPassage_Halo/01Collect-Logs-for-CloudPassage-Halo-App

## Building zip archives from source:

* Clone this repo locally and descend into the root directory of the repo.
* Build the container image: `docker build -t halo-sumologic:latest .`
* Export the lambda archives: `docker run -it --rm -v /tmp/halo-sumologic:/var/export halo-sumologic:latest cp -r /var/output/ /var/export/`

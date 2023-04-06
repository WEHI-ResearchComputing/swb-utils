## Service Workbench Utils
This repository contains some handy tools for working with Service Workbench.

### Non-interactive jobs
For running non-interactive jobs, there are scripts that help you call the API and programmatically 
do what you have been doing through the website.

#### Setup
Install dependencies:
```
pip install -r requirements.txt
```

#### Run a script using the tool
The tool can run a script which spins up a workspace and then runs your script on it.

```
python run_job.py  --job=[script to run]
```
Where `script to run` is the script that needs to be run on the workspace. An example of the command is as below:
```
python run_job.py  --job=test_job.sh
```

Assuming that a workspace is already created, you can use the following script
to run a job on that instance.
```
python run_job.py  --job=[script to run] --workspace=[workspace name]
```
An example of that is shown below:
```
python run_job.py --job=test_job.sh --workspace=test-non-int-1680685747
```

**NOTEs**: 
* The script that is run on the workspace needs to be loaded as part of a study that is linked to the workspace.
* Make sure the API key (`bearer_token` in the `config.py` file) is updated everytime you want to use the script.
* Make sure you add a manual shutdown of the instance at the end of your script as below to make sure the instance
stops running in case it loses its connection with the tool:
```
shutdown -h +1 "Gracefully shutting down the workspace after running the script"
```
#### Possible improvements
* The renewal of the API token can be automated.
* The AMI used in the config could be one that has R, and the required R libraries installed.  Makes sure to update the 
`env_config_id` in the config once that is done.
* The process for uploading the script to the study being used could also be automated.

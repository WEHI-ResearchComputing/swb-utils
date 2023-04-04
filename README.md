## Service Workbench Utils
This repository contains some handy tools for working with Service Workbench.

### Non-interactive jobs
For running non-interactive jobs, there are scripts that help you call the API and programmatically 
do what you have been doing through the website.

### Spin up a new workspace
TBD

### Shutdown the workspace
TBD

### Run a script on an existing machine
Assuming that a workspace is already created and is in running state, you can use the following script
to run a non-interactive job on that instance.
```
./run_job.sh [script to run]
```
Where script to run is the script that needs to be run on the workspace. An example of the command is as below:
```
./run_job.sh test_job.sh
```

**NOTE**: The script that is run on the workspace needs to be loaded as part of a study that is linked to the workspace.

Make sure the API key (`bearer_token` in `run_job.sh`) is updated everytime you want to use the script.


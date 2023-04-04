study_file_location=example_data.adat

head $study_file_location -n 10

sleep 10

shutdown -h +1 "Gracefully shutting down the workspace after running the script"

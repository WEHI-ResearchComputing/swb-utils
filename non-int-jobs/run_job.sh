job_to_run=$1

instance_id=h7dnv7rse8 # dev SWB
#instance_id=6xw3zhvop9 # prod SWB

workspace_id=61697a31-ee5a-4c38-8aec-9fd98e8e4220
key_pair_name=test-nabi-2
keypair_file_path=/Users/nabi.rezvani/Downloads/
study_location=studies/test-proteomics
bearer_token=xxxx

echo "Checking the auth key..."

status_code=$(curl -o /dev/null -s -w "%{http_code}\n" 'https://'$instance_id'.execute-api.ap-southeast-2.amazonaws.com/dev/api/user' \
  --header 'Authorization: Bearer '$bearer_token)

if test "$status_code" -ne 200; then
    echo "\nERROR: The auth key is invalid or expired!"
    exit 1
fi
#exit 0

echo "Getting the keypair details for: $key_pair_name"
keypair_id=$(curl --location \
  --request GET 'https://'$instance_id'.execute-api.ap-southeast-2.amazonaws.com/dev/api/key-pairs' \
  --header 'Authorization: Bearer '$bearer_token \
  | jq -r '.[] | select (.name == "'$key_pair_name'") | .id')

echo "Keypair ID is: $keypair_id"

echo "Getting the connection details for workspace: $workspace_id"

conn_id=$(curl --location \
  --request GET 'https://'$instance_id'.execute-api.ap-southeast-2.amazonaws.com/dev/api/workspaces/service-catalog/'$workspace_id'/connections' \
  --header 'Authorization: Bearer '$bearer_token \
  | jq -r '.[].id')

echo "Connection ID is: $conn_id"

echo "Getting the public connection details"
dns_name=$(curl --location \
  --request POST 'https://'$instance_id'.execute-api.ap-southeast-2.amazonaws.com/dev/api/workspaces/service-catalog/'$workspace_id'/connections/'$conn_id'/send-ssh-public-key' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer '$bearer_token \
  --data-raw '{"keyPairId": "'$keypair_id'"}' \
  | jq -r '.networkInterfaces[].publicDnsName')

echo "Connecting to the Public address : $dns_name"

ssh -o StrictHostKeyChecking=no -i "$keypair_file_path/$keypair_id.pem" ec2-user@$dns_name << EOF
  echo "running the job $job_to_run"
  chmod +x study_location/$job_to_run
  sh $study_location/$job_to_run
EOF


import requests
import json
import subprocess
import time
import calendar
import argparse

from config import Config

bearer_token = Config.bearer_token
key_pair_name = Config.key_pair_name
instance_id = Config.instance_id['dev']

env_type_id = Config.env_type_id
env_config_id = Config.env_config_id
project_id = Config.project_id
study_id = Config.study_id
study_location = Config.study_location
keypair_file_path = Config.keypair_file_path

headers = {'Authorization': f'Bearer {bearer_token}', 'Content-Type': 'application/json'}
base_url = f"https://{instance_id}.execute-api.ap-southeast-2.amazonaws.com/dev/api"


def check_auth_key():
    print('Checking the auth key...')

    resp = requests.get(base_url + "/user", headers=headers)
    # print(resp.json(), resp.reason, resp.status_code)
    if resp.status_code != 200:
        print('Invalid or expired API key!')
        raise Exception('AUTH_ERROR')


def create_or_init_workspace(workspace_name):
    ts = str(calendar.timegm(time.gmtime()))
    ws_name = 'test-non-int-' + ts if not workspace_name else workspace_name
    if not workspace_name:
        body = {
            "name": ws_name,
            "envTypeId": env_type_id,
            "envTypeConfigId": env_config_id,
            "description": "Testing programmatic env spin up",
            "projectId": project_id,
            "cidr": "220.240.214.28/32",
            "studyIds": [
                study_id
            ]
        }
        print(f'Creating a workspace {ws_name} with options: {body}')

        resp = requests.post(base_url + '/workspaces/service-catalog', headers=headers, data=json.dumps(body))
        # workspace_id = resp.json()['id']
        print(resp.status_code, resp.reason, resp.json(), resp.history)
    else:
        print(f'Instance {ws_name} already created!')

    return ws_name


def check_workspace_status(ws_name):
    print(f'Checking the instance status for {ws_name}...')
    status = 'PENDING'
    while True:
        resp = requests.get(base_url + '/workspaces/service-catalog', headers=headers)
        matching_ws = [ws for ws in resp.json() if ws['name'] == ws_name][0]
        workspace_id = matching_ws['id']
        status = matching_ws['status']
        print('Status is: ' + status)
        if status in ['PENDING', 'STARTING']:
            time.sleep(30)
        elif status == 'STOPPED':
            print('Workspace is stopped, staring it')
            start_instance(workspace_id)
            time.sleep(30)
        else:
            break
    if status == 'COMPLETED':
        print(f'Workspace created and started up: {workspace_id}')
    else:
        print(f'Workspace {workspace_id} is not is usable state: {status}')
        raise Exception('WORKSPACE_FAILED')
    return workspace_id


def get_key_pair_id(key_pair_name):
    print(f"Getting the keypair details for: {key_pair_name}")
    resp = requests.get(base_url + "/key-pairs", headers=headers)
    keypair_id = [key for key in resp.json() if key['name'] == key_pair_name][0]['id']

    print(f"Keypair ID is: {keypair_id}")

    return keypair_id


def get_conn_details(workspace_id):
    print(f"Getting the connection details for workspace: {workspace_id}")
    resp = requests.get(base_url + f"/workspaces/service-catalog/{workspace_id}/connections", headers=headers)
    conn_id = resp.json()[0]['id']
    print(f"Connection ID is: {conn_id}")
    return conn_id


def get_dns_details(keypair_id, workspace_id, conn_id):
    print("Getting the public connection details")
    body = {"keyPairId": keypair_id}
    resp = requests.post(
        base_url + f"/workspaces/service-catalog/{workspace_id}/connections/{conn_id}/send-ssh-public-key",
        headers=headers, data=json.dumps(body))
    dns_name = resp.json()['networkInterfaces'][0]['publicDnsName']

    return dns_name


def execute_job(dns_name, keypair_id, job_to_run):
    print(f"Connecting to the Public address : {dns_name}")
    ssh = subprocess.Popen([
        'ssh', '-o StrictHostKeyChecking=no',
        f'-i {keypair_file_path}/{keypair_id}.pem',
        f'ec2-user@{dns_name}'
    ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=0)

    ssh.stdin.write(f'echo "running the job {job_to_run}"\n')
    ssh.stdin.write(f'chmod +x {study_location}/{job_to_run}\n')
    ssh.stdin.write(f'sh {study_location}/{job_to_run}\n')
    ssh.stdin.close()

    print('Output from the workspace:\n')
    for line in ssh.stdout:
        print(line.strip())

    print('Execution completed')


def shutdown_instance(workspace_id):
    print(f'Shutting down the instance: {workspace_id}')
    resp = requests.delete(base_url + f"/workspaces/service-catalog/{workspace_id}", headers=headers)


def start_instance(workspace_id):
    print(f'Starting the instance: {workspace_id}')
    resp = requests.put(base_url + f"/workspaces/service-catalog/{workspace_id}/start", headers=headers)


def run_job(job_to_run, workspace_name, shutdown):
    check_auth_key()

    ws_name = create_or_init_workspace(workspace_name)

    workspace_id = check_workspace_status(ws_name)

    keypair_id = get_key_pair_id(key_pair_name)

    conn_id = get_conn_details(workspace_id)

    dns_name = get_dns_details(keypair_id, workspace_id, conn_id)

    execute_job(dns_name, keypair_id, job_to_run)

    if shutdown:
        shutdown_instance(workspace_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Colonial non-interactive jobs')

    parser.add_argument('-j', '--job', help='The script of the job to run', required=True)
    parser.add_argument('-w', '--workspace', help='The name of the existing workspace to use')
    parser.add_argument('-s', '--shutdown', type=bool, help='Shutdown the instance after running the job', default=True)

    args = parser.parse_args()
    print(f'Running the job with the following parameters: ', args)

    run_job(
        job_to_run=args.job,
        workspace_name=args.workspace,
        shutdown=args.shutdown
    )

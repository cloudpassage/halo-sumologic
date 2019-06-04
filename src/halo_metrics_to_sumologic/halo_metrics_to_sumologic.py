import cloudpassage
import datetime
import json
import os
import re
from sumologic_https import sumologic_https_forwarder


def lambda_handler(event, context):
    print ('[halo_metrics_to_sumologic.lambda_handler][INFO] Starting...')
    max_retry = 3
    sumo_url = os.environ['sumologic_https_url']
    halo_api_key_id = os.environ['halo_api_key_id']
    halo_api_secret = os.environ['halo_api_secret_key']
    integration = get_integration_string()
    print ('Sumo_URL - %s' % sumo_url)
    session = cloudpassage.HaloSession(halo_api_key_id, halo_api_secret, integration_string=integration)
    httphelper = cloudpassage.HttpHelper(session)
    server_groups = cloudpassage.ServerGroup(session)
    root_server_group_id = list({x["id"] for x in server_groups.list_all()
                                 if x["parent_id"] is None})[0]
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print ('[halo_metrics_to_sumologic.lambda_handler][INFO] Current time: %s'
           % current_time)
    # Server count by state
    url = "/v2/servers"
    params = {"group_id": root_server_group_id,
              "state": "active,missing,deactivated,retired",
              "descendants": "true",
              "group_by": "state"}
    servers_by_state_summary = httphelper.get(url, params=params)
    log = {'servers_by_state_summary': servers_by_state_summary}
    data = {'source': 'script',
            'log': log,
            'created_time': current_time}
    sumologic_https_forwarder(url=sumo_url,
                              data=json.dumps(data, ensure_ascii=False),
                              max_retry=max_retry)
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # Issues by criticality
    url = "/v2/issues"
    params = {"group_id": root_server_group_id,
              "descendants": "true",
              "state": "active,deactivated,missing",
              "status": "active",
              "group_by": "issue_type,critical"}
    issues_by_crit = httphelper.get(url, params=params)
    log = {'current_issues_by_criticality_summary': issues_by_crit}
    data = {'source': 'script',
            'log': log,
            'created_time': current_time}
    sumologic_https_forwarder(url=sumo_url,
                              data=json.dumps(data, ensure_ascii=False),
                              max_retry=max_retry)
    # OS types
    url = "/v2/servers"
    params = {"group_id": root_server_group_id,
              "descendants": "true",
              "state": "active",
              "group_by": "os_distribution,os_version"}
    os_types_summary = httphelper.get(url, params=params)
    log = {'os_types_summary': os_types_summary}
    data = {'source': 'script',
            'log': log,
            'created_time': current_time}
    sumologic_https_forwarder(url=sumo_url,
                              data=json.dumps(data, ensure_ascii=False),
                              max_retry=max_retry)
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # SW packages
    url = "/v2/servers"
    params = {"group_id": root_server_group_id,
              "descendants": "true",
              "state": "active,missing,deactivated",
              "group_by": "os_type,package_name,package_version"}
    sw_packages_summary = httphelper.get(url, params=params)
    log = {'sw_packages_summary': sw_packages_summary}
    data = {'source': 'script',
            'log': log,
            'created_time': current_time}
    sumologic_https_forwarder(url=sumo_url,
                              data=json.dumps(data, ensure_ascii=False),
                              max_retry=max_retry)
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # Running processes
    url = "/v2/servers"
    params = {"group_id": root_server_group_id,
              "descendants": "true",
              "state": "active,missing,deactivated",
              "group_by": "os_type,process_name"}
    processes_summary = httphelper.get(url, params=params)
    log = {'processes_summary': processes_summary}
    data = {'source': 'script',
            'log': log,
            'created_time': current_time}
    sumologic_https_forwarder(url=sumo_url,
                              data=json.dumps(data, ensure_ascii=False),
                              max_retry=max_retry)
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # Local server accounts
    url = "/v1/local_accounts"
    params = {"group_id": root_server_group_id,
              "descendants": "true",
              "state": "active,missing,deactivated",
              "group_by": "os_type,username",
              "per_page": "100"}
    local_accounts_summary = httphelper.get(url, params=params)
    # TODO: Test it with more than 100 user accounts.
    log = {'local_accounts_summary': local_accounts_summary}
    data = {'source': 'script',
            'log': log,
            'created_time': current_time}
    sumologic_https_forwarder(url=sumo_url,
                              data=json.dumps(data, ensure_ascii=False),
                              max_retry=max_retry)
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # List SW Vulnerabilities
    url = "/v2/issues"
    params = {"group_id": root_server_group_id,
              "issue_type": "sva",
              "descendants": "true",
              "status": "active",
              "state": "active,missing,deactivated",
              "group_by": "critical,issue_type,rule_key,name,policy_id",
              "sort_by": "critical.desc,count.desc",
              "per_page": "100",
              "page": "1"}
    sw_vulnerability_summary = httphelper.get(url, params=params)
    # TODO: Test it with more than 100 SW vulnerability
    print('SW Vulnerability Summary: %s' % json.dumps(sw_vulnerability_summary,
                                                      indent=2))

    log = {'sw_vulnerability_summary': sw_vulnerability_summary}
    data = {'source': 'script',
            'log': log,
            'created_time': current_time
            }
    sumologic_https_forwarder(url=sumo_url,
                              data=json.dumps(data, ensure_ascii=False),
                              max_retry=max_retry)
    print ("[halo_metrics_to_sumologic.lambda_handler][INFO] End.")
    return current_time

def get_integration_string():
    """Return integration string for this tool."""
    return "Halo-metrics-to-sumologic/%s" % get_tool_version()

def get_tool_version():
    """Get version of this tool from the __init__.py file."""
    here_path = os.path.abspath(os.path.dirname(__file__))
    init_file = os.path.join(here_path, "__init__.py")
    ver = 0
    with open(init_file, 'r') as i_f:
        rx_compiled = re.compile(r"\s*__version__\s*=\s*\"(\S+)\"")
        ver = rx_compiled.search(i_f.read()).group(1)
    return ver


def main():
    lambda_handler('CP Halo Metrics Forwarder - from Halo to Sumo Logic', '')


if __name__ == "__main__":
    main()
import cloudpassage, datetime, json, os
from sumologic_https import sumologic_https_forwarder

def lambda_handler(event, context):
    print ('[halo_metrics_to_sumologic.lambda_handler][INFO] Starting...')
    #print ('Python version: %s' % str(sys.version_info))
    max_retry=3

    sumo_url= os.environ['sumologic_https_url']
    halo_api_key_id = os.environ['halo_api_key_id']
    halo_api_secret = os.environ['halo_api_secret_key']

    print ('Sumo_URL - %s' %sumo_url)
    print ('Halo_api_key - %s' %halo_api_key_id)
    print ('Halo_api_secret - %s' %halo_api_secret)

    session = cloudpassage.HaloSession(halo_api_key_id, halo_api_secret)
    httphelper = cloudpassage.HttpHelper(session)

    server_groups = httphelper.get("/v2/groups")
    root_server_index = next(index for (index, d) in enumerate(server_groups["groups"]) if d["parent_id"] == None)
    #print server_groups["groups"][root_server_index]["id"]
    #print('Server Groups: %s' %json.dumps(server_groups, indent=2))

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print ('[halo_metrics_to_sumologic.lambda_handler][INFO] Current time: %s' % current_time)
    # Server count by state
    #https://portal.cloudpassage.com/v2/servers?group_id=c4bec3800c770132e78d3c764e10c220&state=active,missing,deactivated,retired&descendants=true&group_by=state
    servers_by_state_summary=httphelper.get("/v2/servers?group_id="+server_groups["groups"][root_server_index]["id"]+"&state=active,missing,deactivated,retired&descendants=true&group_by=state")
    '''
    print('Server Count by state: %s' %json.dumps(servers_by_state_summary, indent=2))
    server_count=0
    for each in servers_by_state:
        server_count+=each["count"]
    print ('>> Number of Servers:               %d' % server_count)
    '''
    log = {
        'servers_by_state_summary': servers_by_state_summary,
    }

    data = {'source': 'script',
            'log': log,
            'created_time': current_time
            }
    sumologic_https_forwarder(url=sumo_url, data=json.dumps(data, ensure_ascii=False), max_retry=max_retry)

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # Issues by criticality
    #https://portal.cloudpassage.com/v2/issues?group_id={root_server_group_id}&descendants=true&state=active,deactivated,missing&status=active&group_by=issue_type,critical
    current_issues_by_criticality_summary = httphelper.get("/v2/issues?group_id="+server_groups["groups"][root_server_index]["id"]+"&descendants=true&state=active,deactivated,missing&status=active&group_by=issue_type,critical")
    #print('Current Issues: %s' % json.dumps(current_issues_by_criticality, indent=2))
    '''
    print ('>> Number of Issues:                %d' % current_issues_by_criticality_summary["count"])
    '''
    log = {
        'current_issues_by_criticality_summary': current_issues_by_criticality_summary
    }

    data={'source': 'script',
          'log': log,
          'created_time': current_time
          }
    sumologic_https_forwarder(url=sumo_url, data=json.dumps(data, ensure_ascii=False), max_retry=max_retry)

    # OS types
    #https://portal.cloudpassage.com/v2/servers?group_id={root_server_group_id}&descendants=true&state=active,missing,deactivated&group_by=os_distribution,os_version
    os_types_summary = httphelper.get("/v2/servers?group_id="+server_groups["groups"][root_server_index]["id"]+"&descendants=true&state=active&group_by=os_distribution,os_version")
    #print('OS Types: %s' % json.dumps(num_of_os_types, indent=2))
    '''
    print ('>> Number of OS Types:              %d' % os_types_summary["count"])
    '''
    log = {
        'os_types_summary': os_types_summary
    }

    data={'source': 'script',
          'log': log,
          'created_time': current_time
          }
    sumologic_https_forwarder(url=sumo_url, data=json.dumps(data, ensure_ascii=False), max_retry=max_retry)

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # SW packages
    #https://portal.cloudpassage.com/v2/servers?group_id={root_server_group_id}&descendants=true&state=active,missing,deactivated&group_by=os_type,package_name,package_version
    sw_packages_summary = httphelper.get("/v2/servers?group_id="+server_groups["groups"][root_server_index]["id"]+"&descendants=true&state=active,missing,deactivated&group_by=os_type,package_name,package_version")
    '''
    print('SW Packages: %s' % json.dumps(sw_packages_summary, indent=2))
    num_of_sw_packages = httphelper.get("/v2/servers?group_id="+server_groups["groups"][root_server_index]["id"]+"&descendants=true&state=active,missing,deactivated&group_by=os_type,package_name,package_version")["count"]
    print ('>> Number of SW Packages:           %d' % num_of_sw_packages)
    '''
    log = {
        'sw_packages_summary': sw_packages_summary
    }

    data={'source': 'script',
          'log': log,
          'created_time': current_time
          }
    sumologic_https_forwarder(url=sumo_url, data=json.dumps(data, ensure_ascii=False), max_retry=max_retry)

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # Running processes
    #https://portal.cloudpassage.com/v2/servers?group_id={root_server_group_id}&descendants=true&state=active,missing,deactivated&group_by=os_type,process_name
    processes_summary = httphelper.get("/v2/servers?group_id="+server_groups["groups"][root_server_index]["id"]+"&descendants=true&state=active,missing,deactivated&group_by=os_type,process_name")
    '''
    print('Processes: %s' % json.dumps(processes_summary, indent=2))
    '''
    log = {
        'processes_summary': processes_summary
    }

    data={'source': 'script',
          'log': log,
          'created_time': current_time
          }
    sumologic_https_forwarder(url=sumo_url, data=json.dumps(data, ensure_ascii=False), max_retry=max_retry)

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # Local server accounts
    #https://portal.cloudpassage.com/v1/local_accounts?group_id={root_server_group_id}&descendants=true&group_by=os_type,username&per_page=1
    local_accounts_summary = httphelper.get("/v1/local_accounts?group_id="+server_groups["groups"][root_server_index]["id"]+"&descendants=true&group_by=os_type,username&per_page=100")
    #TODO: Test it with more than 100 user accounts.
    #print('Local server accounts: %s' % json.dumps(local_accounts_summary, indent=2))

    log = {
        'local_accounts_summary': local_accounts_summary
    }

    data={'source': 'script',
          'log': log,
          'created_time': current_time
          }
    sumologic_https_forwarder(url=sumo_url, data=json.dumps(data, ensure_ascii=False), max_retry=max_retry)

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # List SW Vulnerabilities
    # https://portal.cloudpassage.com/v2/issues?group_id={root_server_group_id}&issue_type=sva&per_page=100&page=1&state=active,missing,deactivated&sort_by=critical.desc,count.desc&descendants=true&group_by=critical,issue_type,rule_key,name,policy_id&status=active
    sw_vulnerability_summary = httphelper.get("/v2/issues?group_id=" + server_groups["groups"][root_server_index][
        "id"] + "&issue_type=sva&per_page=100&page=1&state=active,missing,deactivated&sort_by=critical.desc,count.desc&descendants=true&group_by=critical,issue_type,rule_key,name,policy_id&status=active")
    #TODO: Test it with more than 100 SW vulnerability
    print('SW Vulnerability Summary: %s' % json.dumps(sw_vulnerability_summary, indent=2))

    log = {
        'sw_vulnerability_summary': sw_vulnerability_summary
    }

    data = {'source': 'script',
            'log': log,
            'created_time': current_time
            }
    sumologic_https_forwarder(url=sumo_url, data=json.dumps(data, ensure_ascii=False), max_retry=max_retry)
    print ("[halo_metrics_to_sumologic.lambda_handler][INFO] End.")

    return current_time

def main():
  lambda_handler('CP Halo Metrics Forwarder - from Halo to Sumo Logic', '')

if __name__ == "__main__":
    main()
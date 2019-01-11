import datetime
import os
from botocore.exceptions import ClientError
from halo_events import HaloEvents
from manage_state import ManageState
from sumologic_https import sumologic_https_forwarder
from utility import Utility

TIMESTAMP_SSM_PARAM_NAME = '/CloudPassage-SumoLogic/events/timestamp'
SSM_PARAM_DESCRIPTION = 'Timestamp for CloudPassage/Sumologic event shipper.'
AWS_REGION = 'us-west-2'
HALO_CONCURRENCY = 10
MAX_PAGES = 50
SUMO_MAX_RETRY = 3
EXPORT_BATCH_SIZE = 10


def lambda_handler(event, context):
    '''
    :param config: NOT USED
    :param context: NOT USED
    :return: Current time in Zulu format
    '''
    max_retry = SUMO_MAX_RETRY
    sumo_url = os.environ['sumologic_https_url']
    halo_api_key_id = os.environ['halo_api_key_id']
    halo_api_secret = os.environ['halo_api_secret_key']
    halo_events = HaloEvents(halo_api_key_id, halo_api_secret,
                             HALO_CONCURRENCY)
    state_mgr = ManageState(AWS_REGION, TIMESTAMP_SSM_PARAM_NAME,
                            SSM_PARAM_DESCRIPTION)

    invoke_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    try:
        since = state_mgr.get_timestamp()
    except ClientError as e:
        print("Error on retrieval of starting timestamp from AWS SSM:")
        print(e)
        print("Setting timestamp in SSM to now and exiting.")
        state_mgr.set_timestamp(invoke_time)
        return
    until = invoke_time
    print ('Since = %s\n[lambda_handler] Until = %s' % (since, until))
    # List events
    list_of_events = halo_events.get_all_event_pages(since, until, MAX_PAGES)
    print('Number of events: %d' % len(list_of_events))
    if list_of_events:
        shipped_template = "Events between {} and {} shipped to Sumologic"
        fin_msg = shipped_template.format(list_of_events[0]["created_at"],
                                          list_of_events[-1]["created_at"])
        print("Generating event batches.")
        batches = Utility.generate_batches(EXPORT_BATCH_SIZE, list_of_events)
        print("Generated {} batches of events.".format(len(batches)))
        for payload in batches:
            data, last_event_created_at = payload
            sumologic_https_forwarder(url=sumo_url, data=data,
                                      max_retry=max_retry)
            state_mgr.increment_timestamp(last_event_created_at)
        print(fin_msg)
    else:
        last_event_created_at = invoke_time
    # update the last time the script ran with the create_at of last event
    state_mgr.set_timestamp(last_event_created_at)
    print("The new since time (create_at of the last event) - %s" %
          last_event_created_at)
    return invoke_time

import datetime
import os
import json
import boto3
from botocore.exceptions import ClientError
from halo_events import HaloEvents
from sumologic_https import sumologic_https_forwarder

TIMESTAMP_SSM_PARAM_NAME = '/CloudPassage-SumoLogic/events/timestamp'
SSM_PARAM_DESCRIPTION = 'Timestamp for CloudPassage/Sumologic event shipper.'
AWS_REGION = 'us-west-2'
HALO_CONCURRENCY = 10
MAX_PAGES = 50
SUMO_MAX_RETRY = 3
EXPORT_BATCH_SIZE = 10


def get_timestamp():
    ssm_client = boto3.client('ssm', region_name=AWS_REGION)
    param = ssm_client.get_parameter(Name=TIMESTAMP_SSM_PARAM_NAME)
    timestamp = param['Parameter']['Value']
    return timestamp


def set_timestamp(timestamp):
    """Delete and re-create SSM parameter."""
    ssm_client = boto3.client('ssm', region_name=AWS_REGION)
    try:
        # We do this so that we won't exceed the max number of param versions
        ssm_client.delete_parameter(Name=TIMESTAMP_SSM_PARAM_NAME)
    except ClientError as e:
        msg = "Exception when attempting to remove old timestamp from SSM: {}"
        print(msg.format(e))
    response = ssm_client.put_parameter(Name=TIMESTAMP_SSM_PARAM_NAME,
                                        Description=SSM_PARAM_DESCRIPTION,
                                        Value=timestamp, Type='String',
                                        Overwrite=True)
    msg = 'Updated timestamp parameter named {} with {} (version {})'
    print(msg.format(TIMESTAMP_SSM_PARAM_NAME, timestamp, response['Version']))
    return


def increment_timestamp(timestamp):
    """Only update SSM parameter ()faster than delete/re-create."""
    ssm_client = boto3.client('ssm', region_name=AWS_REGION)
    response = ssm_client.put_parameter(Name=TIMESTAMP_SSM_PARAM_NAME,
                                        Description=SSM_PARAM_DESCRIPTION,
                                        Value=timestamp, Type='String',
                                        Overwrite=True)
    msg = 'Updated timestamp parameter named {} with {} (version {})'
    print(msg.format(TIMESTAMP_SSM_PARAM_NAME, timestamp, response['Version']))
    return


def generate_payload(event_list):
    """Generates and sanitizes payload for Sumo."""
    payload = "\n".join([json.dumps(x, ensure_ascii=False).replace('\n', ' ')
                        for x in event_list])
    return payload


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

    print('Sumo_URL - %s' % sumo_url)

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    try:
        since = get_timestamp()
    except ClientError as e:
        print("Error on retrieval of starting timestamp from AWS SSM:")
        print(e)
        print("Setting timestamp in SSM to now and exiting.")
        set_timestamp(current_time)
        return
    until = current_time
    print ('Since = %s\n[lambda_handler] Until = %s' % (since, until))
    # List events
    list_of_events = halo_events.get_all_event_pages(since, until, MAX_PAGES)
    print('Number of events: %d' % len(list_of_events))
    if len(list_of_events) > 0:
        last_event_created_at = list_of_events[-1]['created_at']
        export_counter = 0
        event_accumulator = []
        for event in list_of_events:
            export_counter += 1
            event_accumulator.append(event)
            # When we reach batch size, we dump to Sumo, update timestamp,
            # and empty the event accumulator
            if export_counter % EXPORT_BATCH_SIZE == 0:
                payload = generate_payload(event_accumulator)
                sumologic_https_forwarder(url=sumo_url, data=payload,
                                          max_retry=max_retry)
                event_accumulator = []
                increment_timestamp(event["created_at"])
        # Finally, flush the last partial batch
        payload = generate_payload(event_accumulator)
        if payload != "":
            sumologic_https_forwarder(url=sumo_url, data=payload,
                                      max_retry=max_retry)
        msg = "Events between {} and {} shipped to Sumologic"
        print(msg.format(list_of_events[0]["created_at"],
                         list_of_events[-1]["created_at"]))
    else:
        last_event_created_at = current_time
    # update the last time the script ran with the create_at of last event
    set_timestamp(last_event_created_at)
    print("The new since time (create_at of the last event) - %s" %
          last_event_created_at)
    return current_time

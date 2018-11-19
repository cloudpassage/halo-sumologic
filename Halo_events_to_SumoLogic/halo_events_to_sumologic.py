#__author__ = CoOlNiCk
import datetime, os, json, boto3, botocore, sys
from operator import itemgetter
from sumologic_https import sumologic_https_forwarder
from cp import *


print('[CoOlNiCk] Loading Lambda function - Get Since & Until timestamps')


def create_queue(client, name, fifo):
  print ('[create_queue] Creating Queue (Queue name: %s)' % name)

  try:
    if fifo == 'true':
      # Crete FiFo Queue.  Use ContentBasedDeduplication.
      response = client.create_queue(QueueName=name+'.fifo', Attributes = {'FifoQueue': 'true',
                                                                           'ContentBasedDeduplication': 'true'})
    else:
      # Create regular Queue
      response = client.create_queue(QueueName=name)
    print ('[create_queue] Queue created (Queue name: %s) - Queue URL: %s' % (name, response['QueueUrl']))
    return response

  except botocore.exceptions.ClientError as e:
    print ('[create_queue] Error while creating queue (Queue name: %s) - %s' % (name, e.response['Error']['Code']))
    sys.exit(1)


def enqueue (sqs, queue_url, message, message_group_id=''):
  print ('[enqueue] Enqueue message (Queue URL: %s) - Message: %s' %(queue_url, message))
  try:
    #queue = sqs.get_queue_by_name(QueueName=queue_name)
    if message_group_id == '':
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=0,
            MessageAttributes={},
            MessageBody=message
        )
    else:
      print ('MessageGroupId: %s' %message_group_id)
      response = sqs.send_message(
          QueueUrl=queue_url,
          DelaySeconds=0,
          MessageAttributes={},
          MessageBody=message,
          MessageGroupId=message_group_id
      )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
      print ('[lambda_handler] Error putting message to the queue (Error code - %d)'
             % response['ResponseMetadata']['HTTPStatusCode'])
      print ('[lambda_handler] Response for send_message - HTTPStatusCode: %d (Message: %s)'
             % (response['ResponseMetadata']['HTTPStatusCode'], message))
    return response

  except Exception as e:
    print ('[enqueue] Error while adding message to the queue (Queue URL: %s) - Message: %s' %(queue_url, message))
    print ('[enqueue] Error message - %s' % e)
    sys.exit(1)


def dequeue(sqs, queue_url):
  print ('[dequeue] Dequeue message (Queue URL: %s)' % queue_url)
  try:
      # queue=sqs.get_queue_by_name(QueueName=queue_name)
      response = sqs.receive_message(
          QueueUrl=queue_url,
          AttributeNames=[],
          MaxNumberOfMessages=1,
          MessageAttributeNames=[],
          VisibilityTimeout=0,
          WaitTimeSeconds=0
      )
      print ('[dequeue] Length of the queue: %d' % len(response['Messages']))

      if len(response['Messages']) == 1:
          return response
      elif len(response['Messages']) == 0:
          print ('[dequeue] No message to retrieve from the queue. Error!!')
          sys.exit(1)
      else:
          print ('[dequeue] More than 1 message found from the queue. Error!!')
          sys.exit(1)

  except Exception as e:
      print ('[dequeue] Error while getting message from the queue (Queue URL: %s)' % queue_url)
      print ('[dequeue] Error message - %s' % e)
      sys.exit(1)


def delete_message(sqs, receipt_handle, queue_url):
  print ('[delete_message] Delete message (Queue URL: %s) - Receipt Handle ID: %s' % (queue_url, receipt_handle))
  response = sqs.delete_message(
      QueueUrl=queue_url,
      ReceiptHandle=receipt_handle
  )
  return response


def pull_halo_events(halo_api_key, halo_api_secret, since, until, debug=True):
  print ('[pull_halo_events] Starting to pull events from Halo')
  session = cloudpassage.HaloSession(halo_api_key, halo_api_secret)
  if debug: print ('[pull_halo_events] HaloSession - %s' %session)
  events = cloudpassage.Event(session)
  if debug: print ('[pull_halo_events] HaloEvent - %s' %events)
  list_of_events=events.list_all(pages=100, since=since, until=until)
  return list_of_events


def lambda_handler(event, context):
    #print('Received event: " + json.dumps(event, indent=2))
    '''
    :param config: NOT USED
    :param context: NOT USED
    :return: Current time in Zulu format
    '''
    max_retry=3

    '''
    current_directory = os.path.dirname(os.path.abspath(__file__))

    config = json.loads(open(current_directory + '/halo_config.json', 'r').read())

    sumo_config=json.loads(open(current_directory +'/sumo_config.json', 'r').read())
    '''
    sumo_url= os.environ['sumologic_https_url']
    halo_api_key_id = os.environ['halo_api_key_id']
    halo_api_secret = os.environ['halo_api_secret_key']

    print ('Sumo_URL - %s' %sumo_url)
    print ('Halo_api_key - %s' %halo_api_key_id)
    print ('Halo_api_secret - %s' %halo_api_secret)

    timestamp_queue = 'halo_last_time_ran-test'

    client = boto3.client('sqs', region_name='us-west-2')
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


    try:
        response = client.get_queue_url(QueueName=timestamp_queue)
        # Get the queue. This returns an SQS.Queue instance
        # queue = sqs.get_queue_by_name(QueueName=queue_name)
        queue_url = response['QueueUrl']
        print ('[lambda_handler] Queue found (Queue URL: %s)' % queue_url)
        # Dequeue to get the last time the lambda function was ran
        response = dequeue(client, queue_url=queue_url)
        since = response['Messages'][0]['Body']
        receipt_handle = response['Messages'][0]['ReceiptHandle']
        until = current_time
        print ('[lambda_handler] Since = %s\n[lambda_handler] Until = %s' % (since, until))

        # List events
        list_of_events=pull_halo_events(halo_api_key_id, halo_api_secret, since, until)
        print('[lambda_handler] Number of events: %d' % len(list_of_events))

        if len(list_of_events) > 0:
            ordered_list_of_events = sorted(list_of_events, key=itemgetter('created_at'))
            last_event_created_at = ordered_list_of_events[-1]['created_at']

            for each in ordered_list_of_events:
                print('>>\n\t%s' % each)
                sumologic_https_forwarder(url=sumo_url, data=json.dumps(each, ensure_ascii=False), max_retry=max_retry)
            print(
            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        else:
            last_event_created_at = current_time

        response=delete_message(client, receipt_handle=receipt_handle, queue_url=queue_url)
        print("Delete Response - %s" %response)

        # update the last time the script ran with the create_at of the last event
        enqueue(client, queue_url=queue_url, message=last_event_created_at)
        print("The new since time (create_at of the last event) - %s" %last_event_created_at)

    except botocore.exceptions.ClientError as e:
        if 'NonExistentQueue'  in e.response['Error']['Code']:
            # Queue doesn't exist.  Create Queue.
            response = create_queue(client, name=timestamp_queue, fifo='false')
            enqueue(client, queue_url=response['QueueUrl'], message=current_time)

    return current_time


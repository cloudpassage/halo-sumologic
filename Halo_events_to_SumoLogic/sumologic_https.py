import requests, sys

def sumologic_https_forwarder (url, data, max_retry=3):
  reply = requests.post(url, data=data)
  print (">> Reply Status Code = %s" % reply.status_code)
  reply_status_code=reply.status_code
  num_attempts = 1

  while (reply_status_code != 200) and (num_attempts<max_retry):
    reply = requests.post(url,data=data)
    print (">> RETRYING... REPLY = %s" % reply.status_code)
    reply_status_code=reply.status_code
    num_attempts+=1
    if num_attempts == 3:
      print ('[Error] HTTPS POST to SumoLogic failed (Number of retries - %d)' % num_attempts)
      sys.exit(1)
  return True
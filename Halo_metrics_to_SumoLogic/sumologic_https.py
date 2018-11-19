import requests, sys, ssl

def sumologic_https_forwarder (url, data, max_retry=3):
  print('[sumologic_https.sumologic_https_forwarder][INFO] Starting...')
  reply = requests.post(url, data=data, verify=False)
  print ("[sumologic_https.sumologic_https_forwarder][INFO] Reply Status Code = %s" % reply.status_code)
  reply_status_code=reply.status_code
  num_attempts = 1

  while (reply_status_code != 200) and (num_attempts<max_retry):
    reply = requests.post(url,data=data)
    print ("[sumologic_https.sumologic_https_forwarder][INFO] RETRYING... REPLY = %s" % reply.status_code)
    reply_status_code=reply.status_code
    num_attempts+=1
    if num_attempts == 3:
      print ('[sumologic_https.sumologic_https_forwarder][Error] HTTPS POST to SumoLogic failed (Number of retries - %d)' % num_attempts)
      sys.exit(1)
  return reply_status_code






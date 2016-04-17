import json
import os

# determine environment (e.g. by looking for environment variable PYTHONHOME => /app/.heroku/python)

# local settings for local development (should stay out of GIT)
try:
    from local_config import *
except ImportError as e:
    pass

SQL_INCREMENT_COUNTER="""UPDATE request_recorder SET current_request_count = current_request_count + 1 WHERE timestamp = %s """
SQL_SELECT_ALL="""SELECT ID, timestamp, current_request_count, max_possible_count FROM request_recorder """

# production
if 'VCAP_SERVICES' in os.environ.keys():
    memcachedcloud_service = json.loads(os.environ['VCAP_SERVICES'])['memcachedcloud'][0]
    memcached_credentials = memcachedcloud_service['credentials']

    #print "Memcached_Credentials: "+str(memcached_credentials)

    memcachedURL=str(memcached_credentials['servers']).split(',')[0]
    memcachedUsername=str(memcached_credentials['username'])
    memcachedPassword=str(memcached_credentials['password'])


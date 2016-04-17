import json
import os

# determine environment (e.g. by looking for environment variable PYTHONHOME => /app/.heroku/python)

# local settings for local development (should stay out of GIT)
try:
    from local_config import *
except ImportError as e:
    pass

maxAmountOfCalls=500

SQL_INCREMENT_COUNTER="""UPDATE request_recorder SET current_request_count = current_request_count + 1 WHERE timestamp = %s """
SQL_SELECT_ALL="""SELECT ID, timestamp, current_request_count, max_possible_count FROM request_recorder """

# production
if 'VCAP_SERVICES' in os.environ.keys():
    # URL
    destinationURL='http://'+str(json.loads(os.environ['VCAP_APPLICATION'])['application_uris'][0])+'/receiver'

    # Memcached
    memcachedcloud_service = json.loads(os.environ['VCAP_SERVICES'])['memcachedcloud'][0]
    memcached_credentials = memcachedcloud_service['credentials']

    memcachedURL=str(memcached_credentials['servers']).split(',')[0]
    memcachedUsername=str(memcached_credentials['username'])
    memcachedPassword=str(memcached_credentials['password'])

    # MySQL database (ClearDB)
    cleardb_service = json.loads(os.environ['VCAP_SERVICES'])['cleardb'][0]
    cleardb_credentials = cleardb_service['credentials']

    database_host = str(cleardb_credentials['hostname'])
    database_name = str(cleardb_credentials['name'])
    database_username = str(cleardb_credentials['username'])
    database_password = str(cleardb_credentials['password'])


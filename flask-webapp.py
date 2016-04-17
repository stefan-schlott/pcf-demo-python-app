import os
import bmemcached
import config
from flask import Flask, render_template, redirect, url_for, request, jsonify
import mysql.connector
from forms.senderform import SenderForm
import time

app = Flask(__name__)
# key required by Flask-WTF (for CSRF Protection)
app.config['SECRET_KEY'] = 'very, very secret key'

# little Hello World overview page showing the instance index and the environment variables
@app.route('/', methods=['GET'])
@app.route('/overview', methods=['GET'])
def overview():
    instance_index = os.getenv('INSTANCE_INDEX')

    contentText = 'Hello World. My index is ' + str(instance_index) + ' and here are my environment variables : </br></br>'

    for key in os.environ.keys():
        contentText += str(key) + ' => ' + str(os.environ[key]) + '</br> \n'

    return render_template('overview.html',title='Overview',content=contentText)


# Sender Overview (set the amount of calls to be made by the request worker)
@app.route('/sender', methods=['GET','POST'])
def sender():
    url = None
    amountOfCalls = None
    workInProgress = False

    # use the memcached store to signal the request worker
    mc = bmemcached.Client(config.memcachedURL, config.memcachedUsername, config.memcachedPassword)

    if mc.get('workInProgress'):
        workInProgress = True

    # stop right here until the worker is finished
    if workInProgress:
        return render_template('senderview.html', title='Sender View', busy=workInProgress)

    form = SenderForm(request.form)
    if form.validate_on_submit():
        amountOfCalls = int(form.amountOfCalls.data)

        # check if currently work in progress (worker removes that key after finished business)
        if not workInProgress:
            mc.set('workInProgress','True')
            mc.set('amountOfCalls', str(amountOfCalls))
            mc.set('destinationURL',config.destinationURL)
            workInProgress = True

        return render_template('senderview.html',title='Sender View', busy=workInProgress)
    else:
        return render_template('senderview.html', title='Sender View', form=form)


# API method (no view returned) - for the request worker (incrementing a counter in the database)
@app.route('/receiver', methods=['GET'])
def receiver():
    timestamp = request.args.get('timestamp')
    if timestamp:
        # database connection
        cnx = mysql.connector.connect(user=config.database_username, password=config.database_password,
                                      host=config.database_host, database=config.database_name)
        cursor = cnx.cursor()

        # increase the counter for current_request_count
        cursor.execute(config.SQL_INCREMENT_COUNTER, (timestamp,))

        cnx.commit()

        cursor.close()
        cnx.close()

        print 'Instance Index is: ' + str(os.getenv('INSTANCE_INDEX'))

    return jsonify({})


# overview page for the request run statistics saved in the database
@app.route('/receiver-stats', methods=['GET'])
def receiver_stats():
    request_runs = []

    # database connection
    cnx = mysql.connector.connect(user=config.database_username, password=config.database_password,
                                  host=config.database_host, database=config.database_name)
    cursor = cnx.cursor()

    cursor.execute(config.SQL_SELECT_ALL)

    for (ID, timestamp, current_request_count, max_possible_count) in cursor:

        request_runs.append((ID, time.ctime(timestamp), current_request_count, max_possible_count))

    cursor.close()
    cnx.close()

    return render_template('receiverview.html', title='Receiver View', data=request_runs)


# switching page for the AutoScaler CPU load worker(s)
@app.route('/autoscaler', methods=['GET'])
def autoscaler():
    # either 'ON','OFF' or None
    desiredState=request.args.get('desiredState')
    currentState=None

    mc = bmemcached.Client(config.memcachedURL, config.memcachedUsername, config.memcachedPassword)

    currentState = mc.get('CPULoad')
    print 'CPULoad, Before: '+ str(currentState)

    # initialize, if key does not exist
    if currentState is None:
        mc.add('CPULoad','OFF')

    # set the desired state (if applicable) - expire after 1 hour (in order to reduce unnecessary fake load)
    if desiredState is not None:
        mc.set('CPULoad',str(desiredState), time=3600)

    currentState = mc.get('CPULoad')
    print 'CPULoad, After: '+ str(currentState)

    return render_template('autoscalerview.html', title='Autoscaler View', loadEnabled=currentState)


# quickly clear memcached (for development purposes)
@app.route('/flush-memcached', methods=['GET'])
def flush_memcached():
    mc = bmemcached.Client(config.memcachedURL, config.memcachedUsername, config.memcachedPassword)

    mc.flush_all()

    return redirect(url_for('overview'), code=302)


if __name__ == '__main__':
    # use the Flask default port 5000 if not specified otherwise
    port=int(os.getenv('PORT',5000))

    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)
import os
import bmemcached
import config
from flask import Flask, render_template, redirect, url_for, request

from forms.senderform import SenderForm

app = Flask(__name__)
# key required by Flask-WTF (for CSRF Protection)
app.config['SECRET_KEY'] = 'very, very secret key'

@app.route('/', methods=['GET'])
@app.route('/overview', methods=['GET'])
def overview():
    instance_index = os.getenv('INSTANCE_INDEX')

    contentText = 'Hello World. My index is ' + str(instance_index) + ' and here are my environment variables : </br></br>'

    for key in os.environ.keys():
        contentText += str(key) + ' => ' + str(os.environ[key]) + '</br> \n'

    return render_template('overview.html',title='Overview',content=contentText)


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
        return render_template('sendingstarted.html', title='Sender View', busy=workInProgress)

    form = SenderForm(request.form)
    if form.validate_on_submit():
        url = str(form.url.data)
        amountOfCalls = int(form.amountOfCalls.data)

        # check if currently work in progress (worker removes that key after finished business)
        if not workInProgress:
            mc.set('workInProgress','True')
            mc.set('destinationURL',url)
            mc.set('amountOfCalls',str(amountOfCalls))
            workInProgress = True

        return render_template('sendingstarted.html',title='Sender View', busy=workInProgress, url=url, amountOfCalls=str(amountOfCalls))
    else:
        return render_template('senderview.html', title='Sender View', form=form)

# API method (no view returned)
@app.route('/receiver', methods=['GET'])
def receiver():
    return render_template('receiverview.html', title='Receiver View')

@app.route('/receiver-stats', methods=['GET'])
def receiver_stats():
    return render_template('receiverview.html', title='Receiver View')


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


@app.route('/flush-memcached', methods=['GET'])
def flush_memcached():
    mc = bmemcached.Client(config.memcachedURL, config.memcachedUsername, config.memcachedPassword)

    mc.flush_all()

    return redirect(url_for('overview'), code=302)


if __name__ == '__main__':
    # use the Flask default port 5000 if not specified otherwise
    port=int(os.getenv('PORT',5000))

    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)
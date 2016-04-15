import os

from flask import Flask, render_template, request

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

    return render_template('overview.html',content=contentText)


@app.route('/sender', methods=['GET','POST'])
def sender():
    url = None
    amountOfCalls = None

    form = SenderForm(request.form)
    if form.validate_on_submit():
        url = str(form.url.data)
        amountOfCalls = int(form.amountOfCalls.data)
        return render_template('sendingstarted.html',url=url, amountOfCalls=str(amountOfCalls))
    else:
        return render_template('senderview.html', form=form)


@app.route('/receiver', methods=['GET','POST'])
def receiver():
    return render_template('receiverview.html')

if __name__ == '__main__':
    # use the Flask default port 5000 if not specified otherwise
    port=int(os.getenv('PORT',5000))

    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)
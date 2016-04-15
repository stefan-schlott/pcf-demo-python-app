from flask import Flask
import os
app = Flask(__name__)

@app.route('/')
def hello_world():
    instance_index = os.getenv('INSTANCE_INDEX')

    returnText = 'Hello World. My index is ' + str(instance_index) + ' and here are my environment variables : </br></br>'

    for key in os.environ.keys():
        returnText += str(key) + ' => ' + str(os.environ[key]) + '</br> \n'


    return returnText

if __name__ == '__main__':
    # use the Flask default port 5000 if not specified otherwise
    port=int(os.getenv('PORT',5000))

    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)
# Let's write your code here!

from flask import Flask , request

app = Flask(__name__)
@app.route("/")
def hello_world():
    return "Hello! TEST"

@app.route("/morning")
def good_morning():
    return "Good morning! TEST"

@app.route("/evening/<firstname>")
def evening(firstname):
    return f"Good evening, {firstname}!"

@app.route("/greetings/<period_of_day>/<firstname>")
def greetings(period_of_day, firstname):
    return f"Good {period_of_day}, {firstname}!"

@app.route("/add/<int:first>/<int:second>")
def add(first, second):
    return str(first + second)

@app.route("/afternoon")
def good_afternoon():
    firstname = request.args['firstname']
    return f"Good morning {firstname}!"

@app.route("/afternoon2")
def good_afternoon2():
    firstname = request.args.get('firstname', 'you creep') # with .get the second entry is the default value here 'you creep', in case the 1st is not input
    return f"Good morning, {firstname}!"

@app.route("/substract")
def difference():
    first = int(request.args.get('first', '0'))
    second = int(request.args.get('second', '0'))
    return str(first - second)  # example: /substract?first=10&second=5  when 2 parameters, separate them with "&""

@app.route("/hello")
def hello_api():
    return {"message": "Hello!", "hey": "I'm an API!", "test": "and it is a TEST"} # we return a dictionary !!
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__) 

@app.route('/')
def hello_world():
    return "Hello World"

api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDb
users = db["Users"]

class Register(Resource):
    def post(self):
        data = request.get_json()

        statusCode = validateData(data, 'register')
        if statusCode != 200:
            return formatResponse(statusCode, "Invalid data")

        password = bcrypt.hashpw(data['password'].encode('utf8'), bcrypt.gensalt())

        users.insert({
            "name"     : data['name'],
            "email"    : data['email'],
            "password" : password,
            "sentence" : "",
            "token"    : 5
        })

        return formatResponse(200, "successfully registered")

class StoreSentence(Resource):
    def post(self):
        data = request.get_json()

        statusCode = validateData(data, 'store sentence')
        if statusCode != 200:
            return formatResponse(statusCode, "Invalid data")

        # verify user credential
        validUser = authenticateUser(data['name'], data['password'])
        if not validUser:
            return formatResponse(301, "User credential did not match")
        
        # count no of tokens and check if token left for store
        tokenCount = countToken(data['name'])

        if tokenCount <= 0:
            return formatResponse(301, "no more token left")

        # store the sentence, take one token away and return 200
        users.update({
            "name" : data['name']
        },
        {
            "$set":{
                "sentence" : data['sentence'],
                "token" : tokenCount - 1
            }
        })

        return formatResponse(200, "Sentence is stored successfully")

class getSentence(Resource):
    def post(self):
        data = request.get_json()

        statusCode = validateData(data, 'get sentence')
        if statusCode != 200:
            return formatResponse(statusCode, "Invalid data")

        # verify user credential
        validUser = authenticateUser(data['name'], data['password'])
        if not validUser:
            return formatResponse(301, "User credential did not match")

        # find the sentence
        sentence = users.find({"name" : data['name']},)[0]["sentence"] # findOne takes one document

        return formatResponse(200, "User sentence: "+sentence)


# internal functions

def authenticateUser(name, password):
    hashedPass = users.find({"name" : name},)[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), hashedPass) == hashedPass:
        return True

    return False

def countToken(name):
    return users.find({"name" : name},)[0]["token"]

def formatResponse(status, message):
    return jsonify({
                "status" : status,
                "msg" : message
            })

def validateData(data, serviceName):
    if(serviceName =='register'):
        if 'name' not in data or 'password' not in data or 'email' not in data:
            return 301

        if(serviceName =='store sentence'):
            if 'name' not in data or 'sentence' not in data or 'password' not in data:
                return 301

        if(serviceName =='get sentence'):
            if 'name' not in data or 'password' not in data:
                return 301

    return 200

# internal functions



# Routing

api.add_resource(Register, '/register')
api.add_resource(StoreSentence, '/store')
api.add_resource(getSentence, '/get-sentence')

# Routing


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0') 





"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

app = Flask(__name__) 

@app.route('/')
def hello_world():
    return "Hello World"

api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.newDb
userNum = db["UserNo"]

userNum.insert({
    'no_of_users' : 0
})

class Visit(Resource):
    def get(self):
        visitCount = userNum.find({})[0]['no_of_users'] + 1
        userNum.update({}, {"$set" : {"no_of_users":visitCount}})

        return str("Hello user: "+str(visitCount))


def validateData(data, serviceName):
    if(serviceName=='add'):
        if 'a' not in data or 'b' not in data:
            return 301

    return 200

class Add(Resource):
    def post(self):
        data = request.get_json()

        statusCode = validateData(data, 'add')
        if(statusCode != 200):
            returnData = {
                'Message' : 'Error Occured',
                'status' : statusCode
            }
            
            return jsonify(returnData)

        returnData = {
            'sum' : data['a'] + data['b'],
            'status' : 200
        }

        return jsonify(returnData)

api.add_resource(Add, '/add')
api.add_resource(Visit, '/hello')

# @app.route('/add', methods=['POST'])
# def addNumbers():
#     data = request.get_json()
#     if 'a' not in data:
#         return "No a"
        
#     return jsonify(data['a'] + data['b'])

 
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0') 

"""
from flask import Flask
import requests
import os
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foods.db"
db = SQLAlchemy(app)

base_url = 'https://api.edamam.com/api/food-database/v2/parser'
app_key = os.getenv('EDAMAM_API_KEY')
app_ID = os.getenv('EDAMAM_API_ID')

def construct_food(json_data):
  for i in len(json_data) - 1:
    Food(
      name = json_data[i]['food']['label'],
      energy = json_data[i]['food']['nutrients']['ENERC_KCAL'],
      protein = json_data[i]['food']['nutrients']['PROCNT'],
      carbohydrate = json_data[i]['food']['nutrients']['CHOCDF'],
      fat = json_data[i]['food']['nutrients']['FAT'],
      fiber = json_data[i]['food']['nutrients']['FIBTG']
    )

@app.route('/', defaults={'food' : ''})
@app.route('/<food>', methods= ['GET', 'POST'])
def index(food):
  if food == '':
    return {
    'name' : 'Hello World!'
  }
  else:
    url = f'{base_url}?ingr={food}&app_id={app_ID}&app_key={app_key}'
    response = requests.get(url)
    # response = 200, response.content is the json with \n, \b, etc.
    # data = response.json()['hints']
    # json.loads converts the data into a python object
    json_data = json.loads(response.content)
    print(json_data['hints'])
    return str(json_data)

if __name__ == '__main__':
  app.run(debug=True)
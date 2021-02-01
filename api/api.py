from flask import Flask, request
import requests
import os
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.schema import UniqueConstraint


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foods.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,db)

base_url = 'https://api.edamam.com/api/food-database/v2/parser'
app_key = os.getenv('EDAMAM_API_KEY')
app_ID = os.getenv('EDAMAM_API_ID')

from models import Food, Meal, User

def construct_food(json_data):
  for i in range(len(json_data) - 1):
    # check for unique external id
    external_id = json_data[i]['food']['foodId']
    exists = Food.query.filter_by(external_id=external_id).first()

    if exists is None:
      name = json_data[i]['food']['label']

      energy = json_data[i]['food']['nutrients']['ENERC_KCAL'] if   'ENERC_KCAL' in json_data[i]['food']['nutrients'].keys()  else 0

      protein = json_data[i]['food']['nutrients']['PROCNT'] if  'PROCNT' in json_data[i]['food']['nutrients'].keys() else 0

      carbohydrate = json_data[i]['food']['nutrients']['CHOCDF']  if 'CHOCDF' in json_data[i]['food']['nutrients'].keys() else   0

      fat = json_data[i]['food']['nutrients']['FAT'] if 'FAT' in  json_data[i]['food']['nutrients'].keys() else 0

      fiber = json_data[i]['food']['nutrients']['FIBTG'] if   'FIBTG' in json_data[i]['food']['nutrients'].keys() else 0

      external_id = json_data[i]['food']['foodId']

      food = Food(name=name, energy=energy, protein=protein,  carbohydrate=carbohydrate, fat=fat, fiber=fiber,   external_id=external_id)
      db.session.add(food)
      db.session.commit()
      print(f'{food.name} added to database')

    else:
      pass

@app.route('/', defaults={'food' : ''})
@app.route('/<food>', methods= ['GET', 'POST'])
def index(food):
  url = f'{base_url}?ingr={food}&app_id={app_ID}&app_key={app_key}'
  response = requests.get(url)
    # response = 200, response.content is the json with \n, \b, etc.
    # data = response.json()['hints']
    # json.loads converts the data into a python object
  if food == '':
    return {
      'name' : 'Hello World!'
      }
  else:
    if request.method == 'POST':
      if request.is_json:
        data = request.get_json()
        new_food = Food(
          name=data['name'],
          energy=data['energy'],
          protein=data['protein'],
          carbohydrate=data['carbohydrate'],
          fat=data['fat'],
          fiber=data['fiber'])
        db.session.add(new_food)
        db.session.commit()
        return {"message": f'{new_food.name} has been created successfully.'}
      else:
        return {"error": "The request failed."}
    elif request.method == 'GET':
      json_data = json.loads(response.content)
      results = construct_food(json_data['hints'])
      all_foods = Food.query.all()
      foods_list = [
        {
          'id': food.id,
          'name': food.name,
          'energy': food.energy,
          'protein': food.protein,
          'carbohydrate': food.carbohydrate,
          'fat': food.fat,
          'fiber': food.fiber,
          'external_id': food.external_id
        } for food in all_foods]
      return str(foods_list)

if __name__ == '__main__':
  app.run(debug=True)
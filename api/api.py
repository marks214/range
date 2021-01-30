from flask import Flask, request
import requests
import os
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foods.db"
db = SQLAlchemy(app)
migrate = Migrate(app,db)

base_url = 'https://api.edamam.com/api/food-database/v2/parser'
app_key = os.getenv('EDAMAM_API_KEY')
app_ID = os.getenv('EDAMAM_API_ID')

class Food(db.Model):
  __tablename__ = 'foods'

  id = db.Column(db.Integer, primary_key=True)
  # nullable = False means it cannot be empty
  name = db.Column(db.Text, nullable=False)
  energy = db.Column(db.Float, nullable=True)
  protein = db.Column(db.Float, nullable=True)
  carbohydrate = db.Column(db.Float, nullable=True)
  fat = db.Column(db.Float, nullable=True)
  fiber = db.Column(db.Float, nullable=True)

  def __init__(self, name, energy, protein, carbohydrate, fat, fiber):
    self.name = name
    self.energy = energy
    self.protein = protein
    self.carbohydrate = carbohydrate
    self.fat = fat
    self.fiber = fiber

  def __str__(self):
    return f'{self.id} {self.name} {self.energy} {self.protein} {self.carbohydrate} {self.fat} {self.fiber}'


def construct_food(json_data):
  for i in range(len(json_data) - 1):
    name = json_data[i]['food']['label']
    energy = json_data[i]['food']['nutrients']['ENERC_KCAL']
    protein = json_data[i]['food']['nutrients']['PROCNT']
    carbohydrate = json_data[i]['food']['nutrients']['CHOCDF']
    fat = json_data[i]['food']['nutrients']['FAT']
    fiber = 0
    food = Food(name=name, energy=energy, protein=protein, carbohydrate=carbohydrate, fat=fat, fiber=fiber)
    db.session.add(food)
    db.session.commit()
    print(f'{food.name} added to database')

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
      #   json_data = json.loads(response.content)
      # results = construct_food(json_data['hints'])
      # tests = Food.query.all()
      # show = [{
      # "name" : test.name
      # } for test in tests]
      # return str(show)
    elif request.method == 'GET':
      foods = Food.query.all()
      results = [
        {
          'id': food.id,
          'name': food.name,
          'energy': food.energy,
          'protein': food.protein,
          'carbohydrate': food.carbohydrate,
          'fat': food.fat,
          'fiber': food.fiber
        } for food in foods]
      return str(results)

if __name__ == '__main__':
  app.run(debug=True)
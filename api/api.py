from flask import Flask, request, jsonify, json
import requests, uuid, os, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

            energy = json_data[i]['food']['nutrients']['ENERC_KCAL'] if 'ENERC_KCAL' in json_data[i]['food']['nutrients'].keys(
            ) else 0

            protein = json_data[i]['food']['nutrients']['PROCNT'] if 'PROCNT' in json_data[i]['food']['nutrients'].keys(
            ) else 0

            carbohydrate = json_data[i]['food']['nutrients']['CHOCDF'] if 'CHOCDF' in json_data[i]['food']['nutrients'].keys(
            ) else 0

            fat = json_data[i]['food']['nutrients']['FAT'] if 'FAT' in json_data[i]['food']['nutrients'].keys(
            ) else 0

            fiber = json_data[i]['food']['nutrients']['FIBTG'] if 'FIBTG' in json_data[i]['food']['nutrients'].keys(
            ) else 0

            external_id = json_data[i]['food']['foodId']

            food = Food(name=name, energy=energy, protein=protein,
                        carbohydrate=carbohydrate, fat=fat, fiber=fiber,   external_id=external_id)
            db.session.add(food)
            db.session.commit()
            print(f'{food.name} added to database')

        else:
            pass

def food_serializer(food):
    return {
        'id': food.id,
        'name': food.name,
        'energy': food.energy,
        'protein': food.protein,
        'carbohydrate': food.carbohydrate,
        'fat': food.fat,
        'fiber': food.fiber,
        'external_id': food.external_id
    }


@app.route('/', methods=['GET', 'POST'], defaults={'food': ''})
@app.route('/<food>', methods=['GET', 'POST'])
def index(food):
    if food == '':
        pass
    if request.method == 'GET':
        search_results = Food.query.filter(Food.name.ilike(f'%{food}%')).all()
        if len(search_results) == 0:
            url = f'{base_url}?ingr={food}&app_id={app_ID}&app_key={app_key}'
            response = requests.get(url)
            data = response.json()['hints']
            found_foods = construct_food(data)
            food_matches = Food.query.filter(Food.name.ilike(f'%{food}%')).all()
            return jsonify([*map(food_serializer, food_matches)])
        elif len(search_results) > 0:
            return jsonify([*map(food_serializer, search_results)])
        else:
          pass

    elif request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data['name']
            new_food = Food(
                external_id=f'{name}{uuid.uuid1()}',
                name=name,
                energy=int(data['energy']),
                protein=int(data['protein']),
                carbohydrate=int(data['carbohydrate']),
                fat=int(data['fat']),
                fiber=int(data['fiber']))
            db.session.add(new_food)
            db.session.commit()
            recently_added = Food.query.filter_by(name=new_food.name)
            return jsonify([*map(food_serializer, recently_added)])
        else:
            return {"error": "The request failed."}


if __name__ == '__main__':
    app.run(debug=True)

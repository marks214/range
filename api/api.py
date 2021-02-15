from flask import Flask, request, jsonify, json
import requests, uuid, os, json, secrets, configparser
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt

application = Flask(__name__)
CORS(application)
config = configparser.ConfigParser()
config.read('secrets.ini')

base_url = 'https://api.edamam.com/api/food-database/v2/parser'
application_key = config['api_keys']['EDAMAM_API_KEY']
application_ID = config['api_keys']['EDAMAM_API_ID']

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SECRET_KEY'] = config['secret_key']['SECRET_KEY']
application.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
application.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
application.config["SQLALCHEMY_DATABASE_URI"] = config['postgresql']['POSTGRESDB']

application.config['COGNITO_REGION'] = 'us-west-2'
application.config['COGNITO_USERPOOL_ID'] = config['cognito']['AWS_COGNITO_USER_POOL_ID']
application.config['COGNITO_JWT_HEADER_NAME'] = 'Authorization'

from flask_cognito import CognitoAuth
cogauth = CognitoAuth(application)


db = SQLAlchemy(application)
from models import Food, Meal, User

db.init_app(application)
migrate = Migrate(application, db)

################ USER MODEL RELATED ################
def get_current_user():
    username = current_cognito_jwt['username']
    print('username:', username)
    user = User.query.filter_by(username=username).first()
    print(user)
    return user

def user_serializer(user):
    return {
        'id': user.id,
        'username': user.username,
        'energy_min': user.energy_min,
        'energy_max': user.energy_max,
        'protein_min': user.protein_min,
        'protein_max': user.protein_max,
        'carb_min': user.carb_min,
        'carb_max': user.carb_max,
        'fat_min': user.fat_min,
        'fat_max': user.fat_max,
        'fiber_min': user.fiber_min,
        'fiber_max': user.fiber_max,
    }

@application.route('/api/user', methods=['GET', 'POST'])
@cognito_auth_required
def user():
    user = get_current_user()
    if request.method is 'GET':
        return jsonify(user_serializer(user))
    elif request.method is 'POST':
        if request.is_json:
            print('here')
            data = request.get_json()
            energy_min = data['enery_min'] if type(data['energy_min']) is int else user.energy_min
            # updated_user = user.update({
            #     "energy_min" : energy_min
            # })
            db.session.commit()
            return jsonify(user_serializer(user))
        else:
            return {"error": "The request failed."}


################ LOGIN RELATED ################
@cogauth.identity_handler
def lookup_cognito_user(payload):
    """Look up user in our database from Cognito JWT payload."""
    username = payload['username']
    exists = User.query.filter_by(username=username).first()
    if exists is None:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        print(f'{new_user.username} added to database')
        return new_user
    else:
        return exists

################ FOOD MODEL RELATED ################
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

            # Image by <a href="https://pixabay.com/users/daria-yakovleva-3938704/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1898194">Дарья Яковлева</a> from <a href="https://pixabay.com/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=1898194">Pixabay</a>
            image = json_data[i]['food']['image'] if 'image' in json_data[i]['food'].keys() else 'https://cdn.pixabay.com/photo/2016/12/10/21/26/food-1898194_960_720.jpg'

            external_id = json_data[i]['food']['foodId']

            food = Food(name=name, 
            energy=energy, 
            protein=protein,
            carbohydrate=carbohydrate, 
            fat=fat,
            fiber=fiber,
            image=image,
            external_id=external_id)
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
        'image': food.image,
        'external_id': food.external_id
    }

@application.route('/api/food', methods=['GET', 'POST'], defaults={'food': ''})
@application.route('/api/food/<food>', methods=['GET', 'POST'])
@cognito_auth_required
def index(food):
    if food == '':
        return '<h1>WELCOME!</h1>'
    if request.method == 'GET':
        search_results = Food.query.filter(Food.name.ilike(f'%{food}%')).all()
        if len(search_results) == 0:
            url = f'{base_url}?ingr={food}&app_id={application_ID}&app_key={application_key}'
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
                fiber=int(data['fiber']),
                image='https://cdn.pixabay.com/photo/2018/03/28/20/32/food-3270461_960_720.jpg') #hard-coded image: Image by <a href="https://pixabay.com/users/sansoja-8524640/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=3270461">sansoja</a> from <a href="https://pixabay.com/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=3270461">Pixabay</a>
            db.session.add(new_food)
            db.session.commit()
            recently_added = Food.query.filter_by(name=new_food.name)
            return jsonify([*map(food_serializer, recently_added)])
        else:
            return {"error": "The request failed."}


################ MEAL MODEL RELATED ################
def meal_serializer(meal):
    return {
        'id': meal.id,
        'name': meal.name,
        'energy': meal.energy,
        'protein': meal.protein,
        'carbohydrate': meal.carbohydrate,
        'fat': meal.fat,
        'fiber': meal.fiber,
        'time': meal.time
    }
        
@application.route('/api/meal', methods=['GET', 'POST'])
@cognito_auth_required
def meal():
    user = get_current_user()
    user_id = user.id
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data['name']
            new_meal = Meal(
                name=name,
                energy=data['energy'],
                protein=data['protein'],
                carbohydrate=data['carbohydrate'],
                fat=data['fat'],
                fiber=data['fiber'],
                time=datetime.now(),
                food_id=data['id'],
                user_id=user_id
                )
            db.session.add(new_meal)
            db.session.commit()
            recently_added = Meal.query.filter_by(name=new_meal.name)
            return jsonify([*map(meal_serializer, recently_added)])
        else:
            return {"error": "The request failed."}
    elif request.method == 'GET':
        logged_meals = Meal.query.filter_by(user_id=user_id).all()
        return jsonify([*map(meal_serializer, logged_meals)])

@application.route('/api/meals_week', methods=['GET'])
@cognito_auth_required
def meals_week():
    _1_week_ago = datetime.now() - timedelta(days=7)
    weeks_meals = Meal.query.filter(Meal.time > _1_week_ago).all()
    weekly_meals = [*map(meal_serializer, weeks_meals)]
    for entry in weekly_meals:
        # replaces the time-stamp with an integer (1 - 7), where Mon = 1 and Sunday = 7
        entry['time'] = entry['time'].isoweekday()
    return jsonify(weekly_meals)

@application.route('/api/delete_meal', methods=['POST'])
@cognito_auth_required
def delete():
    request_data = json.loads(request.data)
    Meal.query.filter_by(id=request_data['id']).delete()
    db.session.commit()
    logged_meals = Meal.query.all()
    return jsonify([*map(meal_serializer, logged_meals)])

if __name__ == '__main__':
    application.run(debug=True)

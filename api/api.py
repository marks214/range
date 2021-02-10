from flask import Flask, request, jsonify, json, redirect
from flask_awscognito import AWSCognitoAuthentication
import requests, uuid, os, json, secrets, configparser, cognitojwt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_praetorian
import flask_cors
from cryptography.x509 import load_pem_x509_certificate
from datetime import datetime, timedelta

application = Flask(__name__)
config = configparser.ConfigParser()
config.read('secrets.ini')

application.config['AWS_DEFAULT_REGION'] = 'us-west-2'
application.config['AWS_COGNITO_DOMAIN'] = 'rangereveal.auth.us-west-2.amazoncognito.com'
application.config['AWS_COGNITO_USER_POOL_ID'] = config['cognito']['AWS_COGNITO_USER_POOL_ID']
application.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = config['cognito']['AWS_COGNITO_USER_POOL_CLIENT_ID']
application.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = config['cognito']['AWS_COGNITO_USER_POOL_CLIENT_SECRET']
# change later:
application.config['AWS_COGNITO_REDIRECT_URL'] = 'http://localhost:5000/aws_cognito_redirect'

aws_auth = AWSCognitoAuthentication(application)
cors = flask_cors.CORS()

base_url = 'https://api.edamam.com/api/food-database/v2/parser'
application_key = config['api_keys']['EDAMAM_API_KEY']
application_ID = config['api_keys']['EDAMAM_API_ID']

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SECRET_KEY'] = config['secret_key']['SECRET_KEY']
application.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
application.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
application.config["SQLALCHEMY_DATABASE_URI"] = config['postgresql']['POSTGRESDB']
db = SQLAlchemy(application)
from models import Food, Meal, User
# guard.init_app(application, User)

db.init_app(application)
migrate = Migrate(application, db)
cors.init_app(application)

global curr_user
curr_user = None

@application.route('/')
@aws_auth.authentication_required
def index():
    claims = aws_auth.claims # also available through g.cognito_claims
    return jsonify({'claims': claims})

@application.route('/aws_cognito_redirect')
def aws_cognito_redirect():
    access_token = aws_auth.get_access_token(request.args)
    region = application.config['AWS_DEFAULT_REGION']
    user_pool_ID = application.config['AWS_COGNITO_USER_POOL_ID']
    verified_claims: dict = cognitojwt.decode(
        access_token,
        region,
        user_pool_ID,
        app_client_id = application.config['AWS_COGNITO_USER_POOL_CLIENT_ID'],
        testmode=True)
    username = verified_claims['username']
    print('username:', username)
    global curr_user
    curr_user = username
    print(curr_user)
    return jsonify(verified_claims)

@application.route('/api/sign_in')
def sign_in():
    claims = aws_auth.claims
    print(aws_auth.get_sign_in_url())
    return redirect(aws_auth.get_sign_in_url())

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
def food(food):
    claims = aws_auth.claims
    print(jsonify({'claims': claims}))
    access_token = aws_auth.get_access_token(request.args)
    print(jsonify({'access_token': access_token}))
    if food == '':
        return '<h1>WELCOME!</h1>'
    if request.method == 'GET':
        search_results = Food.query.filter(Food.name.ilike(f'%{food}%')).all()
        if len(search_results) == 0:
            url = f'{base_url}?ingr={food}&app_id={str(application_ID)}&app_key={str(application_key)}'
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
@aws_auth.authentication_required
def meal():
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
                user_id=2 # hard-coded as Aimee
                )
            db.session.add(new_meal)
            db.session.commit()
            recently_added = Meal.query.filter_by(name=new_meal.name)
            return jsonify([*map(meal_serializer, recently_added)])
        else:
            return {"error": "The request failed."}
    elif request.method == 'GET':
        logged_meals = Meal.query.all()
        return jsonify([*map(meal_serializer, logged_meals)])

@application.route('/api/meals_week', methods=['GET'])
def meals_week():
    curr_user_id = get_user_id(curr_user)
    _1_week_ago = datetime.now() - timedelta(days=6)
    weeks_meals = Meal.query.filter_by(user_id=curr_user_id).filter(Meal.time >= _1_week_ago).all()
    weekly_meals = [*map(meal_serializer, weeks_meals)]
    for entry in weekly_meals:
        # replaces the time-stamp with an integer (1 - 7), where Mon = 1 and Sunday = 7
        entry['time'] = entry['time'].isoweekday()
    return jsonify(weekly_meals)

@application.route('/api/delete_meal', methods=['POST'])
def delete():
    request_data = json.loads(request.data)
    Meal.query.filter_by(id=request_data['id']).delete()
    db.session.commit()
    logged_meals = Meal.query.all()
    return jsonify([*map(meal_serializer, logged_meals)])

# @application.route('/api/user_graphs', methods=['GET'])
# def user_graphs():
#     meal_data = Meal.query.all()
#     return 

def get_user_id(json_data):
    exists = User.query.filter_by(username=curr_user).first()
    if exists is None:
        new_user = User(
            username=curr_user,
            energy_min=json_data['kcal_min'],
            energy_max = json_data['kcal_max'],
            protein_min = json_data['protein_min'], 
            protein_max = json_data['protein_max'],
            carb_min = json_data['carb_min'],
            carb_max = json_data['carb_max'],
            fat_min = json_data['fat_min'],
            fat_max =json_data['fat_max']
        )
        db.session.add(new_user)
        db.session.commit()
        print(f'{new_user.username} added to database')
        return str(new_user.id)
    else:
        return str(exists.id)

@application.route('/api/curr_user')
def curr_user():
    print("user is: ", curr_user)
    if curr_user is None:
        return jsonify({"message": "no user found"})
    else:
        return jsonify({"message": f"{curr_user} is logged in"})

if __name__ == '__main__':
    application.run(host='localhost', debug=True)

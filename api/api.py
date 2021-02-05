from flask import Flask, request, jsonify, json
import requests, uuid, os, json, secrets
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_praetorian
import flask_cors
from datetime import datetime

app = Flask(__name__)
guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()

base_url = 'https://api.edamam.com/api/food-database/v2/parser'
app_key = os.getenv('EDAMAM_API_KEY')
app_ID = os.getenv('EDAMAM_API_ID')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://dbmasteruser:2BE:K$b(tgRjEi<JHWKeu7|Q7pjiy;_v@ls-86a832d304e8ec639a5771d66a0e55b8d098a550.ck91wsiodwbr.us-west-2.rds.amazonaws.com:5432/postgres'
# os.getenv('POSTGRES')
db = SQLAlchemy(app)
from models import Food, Meal, User
guard.init_app(app, User)

#db.init_app(app)
migrate = Migrate(app, db)
cors.init_app(app)

with app.app_context():
    db.create_all()
    if db.session.query(User).filter_by(username='Aimee').count() < 1:
        db.session.add(User(
          username='Aimee',
          password=guard.hash_password('strongpassword'),
          roles='admin'
		))
    db.session.commit()

# from https://yasoob.me/posts/how-to-setup-and-deploy-jwt-auth-using-react-and-flask/:
@app.route('/api/login', methods=['POST'])
def login():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.
    .. example::
       $ curl http://localhost:5000/api/login -X POST \
         -d '{"username":"Aimee","password":"strongpassword"}'
    """
    req = request.get_json(force=True)
    username = req.get('username', None)
    password = req.get('password', None)
    user = guard.authenticate(username, password)
    ret = {'access_token': guard.encode_jwt_token(user)}
    return ret, 200

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """
    Refreshes an existing JWT by creating a new one that is a copy of the old
    except that it has a refrehsed access expiration.
    .. example::
       $ curl http://localhost:5000/api/refresh -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    print("refresh request")
    old_token = request.get_data()
    new_token = guard.refresh_jwt_token(old_token)
    ret = {'access_token': new_token}
    return ret, 200
  
  
@app.route('/api/protected')
@flask_praetorian.auth_required
def protected():
    """
    A protected endpoint. The auth_required decorator will require a header
    containing a valid JWT
    .. example::
       $ curl http://localhost:5000/api/protected -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    return {'message': f'protected endpoint (allowed user {flask_praetorian.current_user().username})'}

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
        'image': food.image,
        'external_id': food.external_id
    }

@app.route('/api/food', methods=['GET', 'POST'], defaults={'food': ''})
@app.route('/api/food/<food>', methods=['GET', 'POST'])
def index(food):
    if food == '':
        return '<h1>WELCOME!</h1>'
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
                fiber=int(data['fiber']),
                image='https://cdn.pixabay.com/photo/2016/12/10/21/26/food-1898194_960_720.jpg') #hard-coded image
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

@app.route('/api/meal', methods=['GET', 'POST'])
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

@app.route('/api/delete_meal', methods=['POST'])
def delete():
    request_data = json.loads(request.data)
    Meal.query.filter_by(id=request_data['id']).delete()
    db.session.commit()
    logged_meals = Meal.query.all()
    return jsonify([*map(meal_serializer, logged_meals)])

if __name__ == '__main__':
    app.run(debug=True)

from api import db

class Food(db.Model):
    __tablename__ = 'food'

    id = db.Column(db.Integer, primary_key=True)
    # nullable = False means it cannot be empty
    name = db.Column(db.Text, nullable=False)
    energy = db.Column(db.Float, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbohydrate = db.Column(db.Float, nullable=True)
    fat = db.Column(db.Float, nullable=True)
    fiber = db.Column(db.Float, nullable=True)
    external_id = db.Column(db.String, nullable=True, unique=True)
    quantity = db.Column(db.Float, nullable=False)
    image = db.Column(db.String, nullable=False)
    food_meal = db.relationship('Meal', backref='food', uselist=False) #uselist sets up one-to-one instead of one-to-many

    def __init__(self, name, energy, protein, carbohydrate, fat, fiber, external_id, image, quantity):
        self.name = name
        self.energy = energy
        self.protein = protein
        self.carbohydrate = carbohydrate
        self.fat = fat
        self.fiber = fiber
        self.external_id = external_id
        self.image = image
        self.quantity = quantity

    def __str__(self):
        return f'{self.id} {self.name} {self.energy} {self.protein} {self.carbohydrate} {self.fat} {self.fiber} {self.external_id} {self.image} {self.quantity}'


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    roles = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, server_default='true')

    # the following are per day (e.g., minimum grams of protein per day)
    energy_min = db.Column(db.Integer, nullable=True)
    energy_max = db.Column(db.Integer, nullable=True)
    protein_min = db.Column(db.Integer, nullable=True)
    protein_max = db.Column(db.Integer, nullable=True)
    carb_min = db.Column(db.Integer, nullable=True)
    carb_max = db.Column(db.Integer, nullable=True)
    fat_min = db.Column(db.Integer, nullable=True)
    fat_max = db.Column(db.Integer, nullable=True)
    user_meal = db.relationship('Meal', backref='user')

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id
    
    def is_valid(self):
        return self.is_active

    def __repr__(self):
        return '<User %>' % self.username

# a meal is an individual food consumed by the user (meals do not have multiple foods)


class Meal(db.Model):
    __tablename__ = 'meal'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    energy = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Integer, nullable=True)
    carbohydrate = db.Column(db.Integer, nullable=True)
    fat = db.Column(db.Integer, nullable=True)
    fiber = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Meal %r>' % self.name

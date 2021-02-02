from api import db

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
    external_id = db.Column(db.String, nullable=True, unique=True)

    def __init__(self, name, energy, protein, carbohydrate, fat, fiber):
        self.name = name
        self.energy = energy
        self.protein = protein
        self.carbohydrate = carbohydrate
        self.fat = fat
        self.fiber = fiber

    def __str__(self):
        return f'{self.id} {self.name} {self.energy} {self.protein} {self.carbohydrate} {self.fat} {self.fiber} {self.external_id}'


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String, nullable=False, unique=True)
#     password = db.Column(db.String, nullable=False)
#     # the following are per day (e.g., minimum grams of protein per day)
#     energy_min = db.Column(db.Integer, nullable=True)
#     energy_max = db.Column(db.Integer, nullable=True)
#     protein_min = db.Column(db.Integer, nullable=True)
#     protein_max = db.Column(db.Integer, nullable=True)
#     carb_min = db.Column(db.Integer, nullable=True)
#     carb_max = db.Column(db.Integer, nullable=True)
#     fat_min = db.Column(db.Integer, nullable=True)
#     fat_max = db.Column(db.Integer, nullable=True)

#     def __repr__(self):
#         return '<User %>' % self.username

# # a meal is an individual food consumed by the user (meals do not have multiple foods)


# class Meal(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
#     name = db.Column(db.String, nullable=False)
#     energy = db.Column(db.Integer, nullable=True)
#     protein = db.Column(db.Integer, nullable=True)
#     carb = db.Column(db.Integer, nullable=True)
#     fat = db.Column(db.Integer, nullable=True)
#     time = db.Column(db.DateTime, nullable=False)

#     def __repr__(self):
#         return '<Meal %r>' % self.name

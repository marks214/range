# 🍎📊 [Range Reveal](https://www.rangereveal.com/) 📈🫐

### Capstone Project - Aimee Oz - [Ada Developers Academy](https://adadevelopersacademy.org/)

- Range is the backend repository of Range Reveal. 
- [Reveal](https://github.com/marks214/reveal) is the frontend repository.

## Contents
1. [Getting Started](#start) 
2. [Installation Guide](#install)

# <a name="start">Getting Started</a>

# <a name="install">Installation Guide</a>
1. Clone this repository. `git clone https://github.com/marks214/range.git`
2. Navigate to the project directory. `cd range/api`
3. From the project directory set up your flask virtual environment. `python3 -m venv venv`
4. Activate your virtual environment. `source ./venv/bin/activate`
5. Start your backend server. `flask run`

### Stuff You Should Know:
This project uses [Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html) for user management. You will need to setup a user pool.

The relational database is hosted by [Amazon Lightsail](https://aws.amazon.com/lightsail/). I used PostgreSQL version 12.5.

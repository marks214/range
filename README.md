# 🍎📊 [Range Reveal](https://www.rangereveal.com/) 📈🫐

### Capstone Project - Aimee Oz - [Ada Developers Academy](https://adadevelopersacademy.org/)

- Range is the backend repository of Range Reveal. It was deployed with [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/).
- [Reveal](https://github.com/marks214/reveal) is the frontend repository.

## Contents
1. [Getting Started](#start) 
2. [Installation Guide](#install)

# <a name="start">Getting Started</a>
This project uses [Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html) for user management. You will need to setup a user pool.

The relational database is hosted by [Amazon Lightsail](https://aws.amazon.com/lightsail/). I used PostgreSQL version 12.5.

Generate an application key from [Edamam's food database API](https://developer.edamam.com/).

Create a secrets.ini file in the api folder:

<img src="https://user-images.githubusercontent.com/46636425/108263294-e9c4a880-711a-11eb-8f92-abf24adac77e.png" width="400" height="auto"/>


# <a name="install">Installation Guide</a>
1. Clone this repository.   
    `$  git clone https://github.com/marks214/range.git`
2. Navigate to the project directory.   
    `$  git cd range/api`
3. From the project directory set up your flask virtual environment.   
    `$  git python3 -m venv venv`
4. Activate your virtual environment.   
    `$  git source ./venv/bin/activate`
5. Install the requirements.   
    `$  git pip install -r requirements.txt`
6. Start your backend server.   
    `$  git flask run`

### Entity Relationship Diagram
<img src="https://user-images.githubusercontent.com/46636425/108261061-ef6cbf00-7117-11eb-9d1b-af79f0a2be11.png" width="600" height="auto"/>



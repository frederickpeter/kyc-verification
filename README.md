# KYC Verification API

## Overview

KYC Verification backend codebase. Built with:

- Django
- Django REST Framework
- AWS Textract API
- Simple JWT

## Maintainers

- plangepeter@gmail.com

## Getting Started

### Running locally

1. Clone the project
2. Create a virtual environment with any tool of your liking and activate it (we will use virtualenv for this): `virtualenv venv && source venv/bin/activate`
3. Install Dependencies: `pip install -r requirements.txt`
4. Create .env file from .env.example and fill in all the fields
5. Migrate: `python manage.py migrate`
6. Execute the following to start the server: `python manage.py runserver`.


### Deploying To EC2
1. ssh into server
2. create a new user, grant admin privileges so that you can use sudo
3. The next step is setting up a new user account with reduced privileges for day-to-day use. 
4. Copy the ssh key to the new user
5. sudo apt update && sudo apt-get upgrade
6. install required dependencies: sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx
7. Creating the PostgreSQL Database and User
8. Create virtual env and clone project from git
9. Install requirements
10. Create .env file
11. Migrate the database
12. perform collect static
13. create gunicorn service and socket files
14. Configure Nginx to Proxy Pass to Gunicorn


## Project Structure

#### Folder structure

1. `accounts` - a standard Django app that will contain the custom user model and all endpoints
2. `project`- a standard Django project that contains the configuration



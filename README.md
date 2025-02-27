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

## Project Structure

#### Folder structure

1. `accounts` - a standard Django app that will contain the custom user model and all endpoints
2. `project`- a standard Django project that contains the configuration



export FLASK_ENV=Testing
pytest --cov-report html --cov=blueprints tests/
export FLASK_ENV=Production
# ml-django-app

An example of simple Machine Learning (ML) service implemented in Django & DRF (with connection to PostgreSQL) and managed with use of Docker environment. 

### ML part

Currently there are two classifiers: Random Forest Classifier and "Extra Trees" Classifier, which are used to predict whether yearly income exceeds $50k based on "Adult Data Set" available on: https://archive.ics.uci.edu/ml/datasets/adult

#### Making predictions using web service
To make a prediction on provided data sample, we need to:
1. go to `http://0.0.0.0:8000/api/v1/income_classifier/predict`
2. provide data in JSON format, e.g.: 

```
{
    "age": 37,
    "workclass": "Private",
    "fnlwgt": 34146,
    "education": "HS-grad",
    "education-num": 9,
    "marital-status": "Married-civ-spouse",
    "occupation": "Craft-repair",
    "relationship": "Husband",
    "race": "White",
    "sex": "Male",
    "capital-gain": 0,
    "capital-loss": 0,
    "hours-per-week": 68,
    "native-country": "United-States"
}
```
and make a POST. The prediction is calculated for the MLAlgorithm with parent endpoint name (currently available only `income_classifier`), status type (`production` by default) and only if `status__active = True`. There is possibility to pass other parameters to select MLAlgorithm for predicition using query params in url, e.g.: 

`http://0.0.0.0:8000/api/v1/income_classifier/predict?status=testing&version=0.0.1`


### Docker

Docker Compose manages multicontainer structure, which consists of main (web) container, database container and the separate one for jupyter notebook used for convenient data analysis and ML modeling. The `docker-compose.yml` file contains necessary setup. 

To build docker image we need to run:

```
$ docker-compose build
```

and to start the container:

```
$ docker-compose up
```

On the local machine the web server is available on: http://0.0.0.0:8000/api/v1/

To execute django commands related to `manage.py` on running web container, we need to use:

```
$ docker-compose exec web python ./backend/manage.py <OPTION>
```
For example:
 	- To run unit tests:
		```
		$ docker-compose exec web python ./backend/manage.py test apps.ml.tests
		```

	- To run django shell_plus:
		```
		$ docker-compose exec web python ./backend/manage.py shell_plus
		```

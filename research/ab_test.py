
import json
from time import sleep

import numpy as np  # for data manipulation
import pandas as pd
import requests
from sklearn.model_selection import train_test_split

data = pd.read_csv("/code/research/data/adult.csv", skipinitialspace=True)

X = data.drop("income", axis=1)
y = data["income"]
# divide into training and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state=1234)


for i in range(100):
    print(i)
    input_data = dict(X_test.iloc[i])
    target = y_test.iloc[i]
    r = requests.post("http://127.0.0.1:8000/api/v1/income_classifier/predict?status=ab_testing", input_data)
    response = r.json()
    # provide feedback
    print(response)
    requests.put("http://127.0.0.1:8000/api/v1/mlrequests/{}".format(response["request_id"]), {"feedback": target})

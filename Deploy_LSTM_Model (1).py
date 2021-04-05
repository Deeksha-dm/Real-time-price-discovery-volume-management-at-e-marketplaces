# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 17:12:41 2021

@author: alame
"""

import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder
import os
import numpy as np
import mysql.connector as sql



db_connection = sql.connect(host='localhost', database='agri',user='root', password='Prak121!')
#connecting to MYSQL server by providing the databse name and user name and password

db_cursor = db_connection.cursor()
#storing the instance of sql server 

db_cursor.execute('SELECT * FROM agriprice')
#retreiving overall data 

table_rows = db_cursor.fetchall()
#fetching all the rows

data = pd.DataFrame(table_rows)
#converting the fetched data to a dataframe

data.columns=['Date','Amc_Name','Crop','Maximum','Minimum','Model']

lb_amc = LabelEncoder()
lb_crop = LabelEncoder()

data.Amc_Name = lb_amc.fit_transform(data.Amc_Name)
unique_Amc_Nos = data.Amc_Name.unique()
unique_Amc_labels = lb_amc.inverse_transform(data.Amc_Name.unique())
amc_dict = {}
for i in range(len(unique_Amc_labels)):
    amc_dict[unique_Amc_labels[i]] = unique_Amc_Nos[i]
data.Crop = lb_crop.fit_transform(data.Crop)
unique_Crop_Nos = data.Crop.unique()
unique_Crop_labels = lb_crop.inverse_transform(unique_Crop_Nos)
crop_dict = {}
for i in range(len(unique_Crop_labels)):
    crop_dict[unique_Crop_labels[i]] = unique_Crop_Nos[i]
crop_max = data.Crop.max()
crop_min = data.Crop.min()
amc_max = data.Amc_Name.max()
amc_min = data.Amc_Name.min()
max_max = data.Maximum.max()
max_min = data.Maximum.min()
min_max = data.Minimum.max()
min_min = data.Minimum.min()
model_max = data.Model.max()
model_min = data.Model.min()
model_mean = data.Model.mean()

model = load_model(r"C:\Users\prakruthi\Desktop\aichallenge\price_predict_model.h5")



from flask_ngrok import run_with_ngrok
from flask import Flask,jsonify
app =Flask(__name__)
run_with_ngrok(app) #starts ngrok when the app is running
@app.route("/<Amc_Name>/<Crop>/<int:Maximum>/<int:Minimum>")
def home(Amc_Name,Crop,Maximum,Minimum):
    market = amc_dict.get(Amc_Name)
    crop = crop_dict.get(Crop)
   
    market_scale = np.round(((market - amc_min)/(amc_max- amc_min)),4)
    crop_scale = np.round(((crop - crop_min)/(crop_max-crop_min)),4)
    maximum_scale = np.round(((Maximum - max_min)/(max_max-max_min)),4)
    minimum_scale = np.round(((Minimum - min_min)/(min_max-min_min)),4)

    X = [market_scale,crop_scale, maximum_scale, minimum_scale]
    X = np.array(X).reshape(-1,4)
    X = X.reshape((X.shape[0], 1,X.shape[1]))

    Y_pred = model.predict(X)

    Y_final = Y_pred*(Maximum-Minimum)+Minimum
    return jsonify(str(Y_final[0][0]))
app.run()


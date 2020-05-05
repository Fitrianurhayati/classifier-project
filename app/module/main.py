from flask import render_template, request
from app import app
import os


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/predict', methods=['GET','POST'])   
def predict():
	if request.method =="GET":
		return render_template("form.html")
	elif request.method =="POST":
		file = request.files['file']

		file.save(os.path.join('app/tmp','data_uji.xlsx'))
		return "OK"
from flask import render_template, request
from app import app
import os
import pandas as pd
from flask import request, render_template
from app.module.classifier import Classifier, append_df_to_excel

global year


@app.route('/')
def index():
	return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == "GET":
		return render_template("form.html")
	elif request.method == "POST":
		# define global variable
		global year
		year = request.form['year']
		file = request.files['file']

		file.save(os.path.join('app/tmp', 'data_uji.xlsx'))
		df = pd.read_excel("app/tmp/data_uji.xlsx")
		return render_template("view-data.html", tables=[
			df.to_html(classes='table table-striped', border=0, index=False, justify='left')])


@app.route("/predict", methods=['GET'])
def predict():
	# define global variable
	global year

	df = pd.read_excel("app/tmp/data_uji.xlsx")
	# Define object for classifier
	classifier = Classifier(test_data=df)
	classifier.preProcessing()
	prediction = classifier.predict()

	year = year
	append_df_to_excel('app/tmp/result.xlsx', prediction, sheet_name=year, index=False)
	return render_template("hasil-predict.html", tables=[
		prediction.to_html(classes='table table-striped', border=0, index=False, justify='left')])

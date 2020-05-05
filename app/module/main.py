from flask import render_template, request
from app import app
import os
import pandas as pd 
from flask import request, render_template

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['GET','POST'])   
def upload():
	if request.method =="GET":
		return render_template("form.html")
	elif request.method =="POST":
		file = request.files['file']

		file.save(os.path.join('app/tmp','data_uji.xlsx'))
		df = pd.read_excel("app/tmp/data_uji.xlsx")
		return render_template("view-data.html", tables=[df.to_html(classes='table table-striped', border=0,index=False, justify='left')])



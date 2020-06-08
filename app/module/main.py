from app import app
from flask import render_template, request
from flask import request, render_template
from app.module.classifier import Classifier, append_df_to_excel

import os
import pandas as pd
import xlrd

global year


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # define global variableconda deactivate
    if request.method == "GET":
        return render_template("form.html")
    elif request.method == "POST":
        file = request.files['file']

        file.save(os.path.join('app/tmp', 'data_uji.xlsx'))
        message = '<div class="alert alert-success" role="alert">File successfully uploaded</div>'
        return render_template("form.html", message=message)


@app.route('/view-data', methods=['GET', 'POST'])
def view_data():
    # Define global variable
    global year

    xls = xlrd.open_workbook(r'app/tmp/data_uji.xlsx', on_demand=True)
    options = list()
    for sheet_name in xls.sheet_names():
        option = "<option value='{0}'>{0}</option>".format(sheet_name)
        options.append(option)

    if request.method == "GET":
        return render_template("view-data.html", options=options)
    elif request.method == "POST":
        year = request.form['year']
        button = '<a href="/predict" class="btn btn-primary pull-right">Analysis</a>'
        df = pd.read_excel("app/tmp/data_uji.xlsx", sheet_name=year)
        return render_template("view-data.html", options=options, button=button, tables=[
            df.to_html(classes='table table-striped', border=0, index=False, justify='left')])


@app.route("/predict", methods=['GET'])
def predict():
    # Define global variable
    global year

    df = pd.read_excel("app/tmp/data_uji.xlsx", year)
    df = df[['Judul']]
    # Define object for classifier
    classifier = Classifier(test_data=df)
    classifier.preProcessing()
    prediction = classifier.predict()

    year = year
    append_df_to_excel('app/tmp/result.xlsx', prediction, sheet_name=year, index=False)
    return render_template("hasil-predict.html", tables=[
        prediction.to_html(classes='table table-striped', border=0, index=False, justify='left')])


@app.route('/chart', methods=["GET"])
def chart():
    xls = xlrd.open_workbook(r'app/tmp/result.xlsx', on_demand=True)
    relata = list()
    sistem_cerdas = list()
    list_df = list()
    for sheet_name in xls.sheet_names():
        df = pd.read_excel('app/tmp/result.xlsx', sheet_name=sheet_name)
        sistem_cerdas.append(len(df.loc[df['Class'] == 'Sistem Cerdas'].Class))
        relata.append(len(df.loc[df['Class'] == 'Relata'].Class))
        list_df.append(df)

    return render_template('chart.html', years=xls.sheet_names(), relata=relata, sistem_cerdas=sistem_cerdas,
                           list_df=list_df)


@app.route('/result', methods=['GET', 'POST'])
def result():
    xls = xlrd.open_workbook(r'app/tmp/result.xlsx', on_demand=True)
    options = list()
    for sheet_name in xls.sheet_names():
        option = "<option value='{0}'>{0}</option>".format(sheet_name)
        options.append(option)

    if request.method == 'GET':
        return render_template('result.html', options=options)
    else:
        year = request.form['year']
        df = pd.read_excel('app/tmp/result.xlsx', sheet_name=year)
        return render_template('result.html', options=options, tables=[df.to_html(classes='table table-striped',
                                                                                  border=0, index=False,
                                                                                  justify='left')])

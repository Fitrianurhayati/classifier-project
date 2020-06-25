from app import app
from flask import render_template, request
from flask import request, render_template
from sklearn.metrics import accuracy_score, precision_score, recall_score
from app.module.classifier import Classifier, append_df_to_excel

import os
import pandas as pd
import statistics
import xlrd

global year


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "GET":
        # define global variable
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
    classifier = Classifier(test_data=df, train_data=pd.read_excel("app/tmp/training.xlsx"))
    classifier.preProcessing()
    prediction = classifier.predict()

    labels = list()
    for label in df['Class']:
        if label == 'Relata':
            labels.append(0)
        else:
            labels.append(1)

    prediction['Label'] = labels

    # Define list for iteration
    iterationTest = list()
    iterationTrain = list()

    # Define divide rows to split data training and data testing
    divideRows = round(len(prediction) / 10)

    # Define head data
    head = 0

    # Define tail data
    tail = divideRows

    # Looping data and get iteration
    for i in range(10):
        iterationTest.append(prediction[head:tail][["Judul", "Label"]])
        iterationTrain.append(prediction.drop(prediction.index[head:tail]))
        head = tail
        tail += divideRows

    # Define list
    accuracy_scores = list()
    precision_scores = list()
    recall_scores = list()

    for i in range(10):
        classifier = Classifier(test_data=iterationTest[i], train_data=iterationTrain[i])
        classifier.preProcessing()
        predict = classifier.pengujian()
        actual = iterationTest[i].Label.tolist()
        accuracy_scores.append(accuracy_score(actual, predict))
        precision_scores.append(precision_score(actual, predict))
        recall_scores.append(recall_score(actual, predict))

    year = year
    append_df_to_excel('app/tmp/result.xlsx', prediction, sheet_name=year, index=False)

    df = prediction[['Judul','Preprocessing', 'Class']]
    return render_template("hasil-predict.html", tables=[
        df.to_html(classes='table table-striped', border=0, index=False, justify='left')], year=year,
                           accuracy=round(statistics.mean(accuracy_scores), 2) * 100,
                           precision=round(statistics.mean(precision_scores), 2) * 100,
                           recall=round(statistics.mean(recall_scores), 2) * 100)


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

    # Accuracy, precision and recall
    dataset = pd.read_excel("app/tmp/hasil-dataset.xlsx")

    # Define list for iteration
    iterationTest = list()
    iterationTrain = list()

    # Define divide rows to split data training and data testing
    divideRows = round(len(dataset) / 10)

    # Define head data
    head = 0

    # Define tail data
    tail = divideRows

    # Looping data and get iteration
    for i in range(10):
        iterationTest.append(dataset[head:tail][["Judul", "Label"]])
        iterationTrain.append(dataset.drop(dataset.index[head:tail]))
        head = tail
        tail += divideRows

    # Define list
    accuracy_scores = list()
    precision_scores = list()
    recall_scores = list()

    for i in range(10):
        classifier = Classifier(test_data=iterationTest[i], train_data=iterationTrain[i])
        classifier.preProcessing()
        predict = classifier.pengujian()
        actual = iterationTest[i].Label.tolist()
        accuracy_scores.append(accuracy_score(actual, predict))
        precision_scores.append(precision_score(actual, predict))
        recall_scores.append(recall_score(actual, predict))

    return render_template('chart.html', years=xls.sheet_names(), relata=relata, sistem_cerdas=sistem_cerdas,
                           list_df=list_df, accuracy=round(statistics.mean(accuracy_scores), 2),
                           precision=round(statistics.mean(precision_scores), 2),
                           recall=round(statistics.mean(recall_scores), 2))


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

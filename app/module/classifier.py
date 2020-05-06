# Load library from third party library
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from app.module.slang import stp
from app.module.stopwordku import stopword 

import math
import numpy as np
import nltk
import pandas as pd
import pickle
import re
import statistics 
import sys

# Define variable to use som e library
stemmer = StemmerFactory().create_stemmer()
remover = StopWordRemoverFactory().create_stop_word_remover()
vectorizer = TfidfVectorizer()
naivebayes = MultinomialNB()

# Create class for classifier
class Classifier(object):
    # Define constructor
    def __init__(self, test_data):
        # Define atribute
        self.dataset = pd.read_excel("app/tmp/training.xlsx")
        self.testData = test_data
        self.loadVector = None
        self.loadNB = None

        X = vectorizer.fit_transform(self.dataset.Preprocessing.values.astype('U'))
        naivebayes.fit(X,self.dataset.Label)
        vectorFile = open('app/tmp/vectorizer.b', 'wb')
        nbFile = open('app/tmp/naive_bayes.b', 'wb')
        pickle.dump(vectorizer, vectorFile)
        pickle.dump(naivebayes, nbFile)
        vectorFile.close()  
        nbFile.close() 
        
    def loadPickle(self):
        self.loadVector = pickle.load(open('app/tmp/vectorizer.b', 'rb'), encoding='latin1')
        self.loadNB = pickle.load(open('app/tmp/naive_bayes.b', 'rb'), encoding='latin1')
    
    def preProcessing(self):
        cleanText = list()
        # Loop field Judul to preprocessing
        for text in self.testData['Judul']:
            # Convert to lower case
            text = text.lower()
            # Remove digits
            text = re.sub('\W+', ' ', text)
            # Remove typo
            words = list()
            for word in text.split():
                if word in stp:
                  """
                  Replace word to stp
                  ex: cbc to stp[cbc] value
                  """
                  word = word.replace(word, stp[word])
                words.append(word)
            # Joining words to sentence text
            text = " ".join(words)
            # Stemming
            text = stemmer.stem(text)
            # Filtering
            text = remover.remove(text)
            cleanText.append(text)
        
        self.testData['Preprocessing'] = cleanText
        return self.testData
    
    def predict(self):
        # Load pickle for TF-IDF Vectorizer and Naive Bayes dataset
        self.loadPickle()

        # Define result
        result = list()

        # Get prediction
        termFrequency = self.loadVector.transform(self.testData["Preprocessing"].values.astype('U'))
        for i in termFrequency:
            predict = "Relata" if self.loadNB.predict(i)[0] == 0 else "Sistem Cerdas"
            result.append(predict)

        self.testData["Class"] = result
        return self.testData
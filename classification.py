from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.model_selection import learning_curve
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import pickle


class Classification:

    def __init__(self, dataset_name):
        self.dataset_name = dataset_name

    def train(self, algorithm):
        # get processed train/validation sets
        train_x, train_y, val_x, val_y = self.__load_training_set__()
        # load previous model if any, or create a new model
        classifier = None
        try:
            with open('model/' + algorithm + '.pkl', 'rb') as model:
                classifier = pickle.load(model)
                print('Saved ' + algorithm + ' classification model is loaded.')
        except FileNotFoundError:
            if algorithm == 'dt':
                print('Training Decision Tree Classifier model with new data ......')
                classifier = DecisionTreeClassifier(criterion='entropy', random_state=0)
            elif algorithm == 'nb':
                print('Training Naive Bayes (Gaussian) Classifier model with new data ......')
                classifier = GaussianNB()
            else:
                pass
        # fit training set to classifier model
        classifier.fit(train_x, train_y)
        print('Training finished.')
        # cross-validation
        print('Cross-validating the model ......')
        pred_y = classifier.predict(val_x)
        # show score metrics
        self.__show_score__(val_y, pred_y)
        # retrain the model with validation set
        classifier.fit(val_x, val_y)
        # save the model
        with open('model/' + algorithm + '.pkl', 'wb') as model:
            pickle.dump(classifier, model)
        # show graphical result of training set
        self.__show_learning_curve__(classifier, train_x, train_y)

    def predict(self, algorithm):
        # load test set
        test_x, test_y = self.__load_test_set()
        # load previous model if any, or throw error
        classifier = None
        try:
            with open('model/' + algorithm + '.pkl', 'rb') as model:
                classifier = pickle.load(model)
                print('Saved ' + algorithm + ' classification model is loaded.')
        except FileNotFoundError:
            print('You haven\t train any model yet, please train first.')
            os._exit(1)
        # predict the test set
        print('Predicting the test set ......')
        pred_y = classifier.predict(test_x)
        # show score metrics
        self.__show_score__(test_y, pred_y)

    def __show_score__(self, val_y, pred_y):
        # print metrics
        print('Accuracy', metrics.accuracy_score(val_y, pred_y))
        print('precision_score (micro)', metrics.precision_score(val_y, pred_y, average='micro'))
        print('recall_score (micro)', metrics.recall_score(val_y, pred_y, average='micro'))
        print('f1_score (micro)', metrics.f1_score(val_y, pred_y, average='micro'))

    def __show_learning_curve__(self, model, train_x, train_y, scoring='f1_micro', cv=10):
        # Create CV training and test scores for various training set sizes
        train_sizes, train_scores, test_scores = learning_curve(model,
                                                                train_x,
                                                                train_y,
                                                                # K-fold cross-validation where k set to 10 by default
                                                                cv=cv,
                                                                # use f1 score (micro-average) metric
                                                                scoring=scoring,
                                                                # use all system threads
                                                                n_jobs=-1,
                                                                # set batch size of the training set
                                                                train_sizes=np.linspace(0.01, 1.0, 5))
        # Create means and standard deviations of training set scores
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        # Create means and standard deviations of test set scores
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)
        # Draw lines
        plt.plot(train_sizes, train_mean, color="#330000", label="Training score")
        plt.plot(train_sizes, test_mean, color="#4d94ff", label="Cross-validation score")
        # Draw bands
        plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, color="#DDDDDD")
        plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, color="#DDDDDD")
        # Create plot
        plt.title("Learning Curve")
        plt.xlabel("Training Set Size"), plt.ylabel("F1 Score"), plt.legend(loc="best")
        plt.tight_layout()
        plt.show()

    def __load_training_set__(self):
        try:
            # load training set and validation set, split them into features and output
            train_set = pd.read_csv('data/' + self.dataset_name + '/' + self.dataset_name + 'Train.csv', header=None)
            train_x = train_set.iloc[:, :-1]
            train_y = train_set.iloc[:, -1]
            val_set = pd.read_csv('data/' + self.dataset_name + '/' + self.dataset_name + 'Val.csv', header=None)
            val_x = val_set.iloc[:, :-1]
            val_y = val_set.iloc[:, -1]
            print('The training set and validation set of  ' + self.dataset_name + ' is loaded.')
            print('Instance: ', len(train_set.axes[0]))
            print('Feature: ', len(train_set.axes[1]) - 1)
            return train_x, train_y, val_x, val_y
        except FileNotFoundError:
            print('The data set cannot be found in the data directory, please double check.')
            os._exit(1)

    def __load_test_set(self):
        try:
            # load test set, split them into features and output
            test_set = pd.read_csv('data/' + self.dataset_name + '/' + self.dataset_name + 'Test.csv', header=None)
            test_x = test_set.iloc[:, :-1]
            test_y = test_set.iloc[:, -1]
            print('The test set of ' + self.dataset_name + ' is loaded.')
            print('Instance: ', len(test_set.axes[0]))
            print('Feature: ', len(test_set.axes[1]) - 1)
            return test_x, test_y
        except FileNotFoundError:
            print('The data set cannot be found in the data directory, please double check.')
            os._exit(1)

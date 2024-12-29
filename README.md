# Voice assistant
Voice assistant is an application created in Python.

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Model description](#model-description)

## General info
This is a small Python application which works like a Google Assistant. You give some questions or requests and the assistant helps you.
For now, it can do a to-do list for you or take a screenshot. The process of answering the requests is based on **bag-of-words model**, so
the assistant is not sensitive to a little bit different phrases.

## Technologies
The app was created by using suitable libraries in Python to voice recognition and scikit-learn to train the model.

## Model description
Bag-of-words model in this case is a model of text which is trained on some dataset with phrases and their classes. After that it classifies
the user's phrases to the proper class and then assistant makes adequate instruction. The dataset is small, but it is enough for now.


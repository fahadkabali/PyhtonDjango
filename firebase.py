import pyrebase
import os

config = {
    "apiKey": "AIzaSyCL27LTaGiGxagD7rBsNj_h74740ETvH6Q",
    "authDomain": "csat-d3282.firebaseapp.com",
    "projectId": "csat-d3282",
    "storageBucket": "csat-d3282.appspot.com",
    "messagingSenderId": "873027082625",
    "appId": "1:873027082625:web:98a1139aaa5c507d4d3080",
    "measurementId": "G-MKML67B3K4",
    "databaseURL": ""

}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
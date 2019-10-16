# -*- coding: utf-8 -*-
"""TenSpecies96x96.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16_N4i4shjEFG0IfgQkcxI0K8PK6Ev7rB
"""

from __future__ import absolute_import, division, print_function, unicode_literals

!pip install tensorflow==1.14.0rc1

#!pip install keras==2.2.4
import tensorflow as tf

import imageio
import os
import glob
import csv
import math
from pathlib import Path
import numpy as np
from skimage import io
from skimage import transform
from skimage import draw
from skimage import exposure
import matplotlib.pyplot as plt
import pickle
import requests
import tarfile
import dlib
import sys
from PIL import Image
from PIL.ExifTags import TAGS
!pip install -q tf-nightly
from google.colab import drive
drive.mount('/content/gdrive')
!pip install -U -q PyDrive ## you will have install for every colab session
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
# 1. Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

import errno
import urllib
try:
    from imageio import imsave
except:
    from scipy.misc import imsave

!ls "/content/gdrive/My Drive/"
import tarfile
"""
!unzip -q "/content/gdrive/My Drive/stl10-dataset.zip"
!unzip -q "test_images.zip"
!unzip -q "train_images.zip"
!unzip -q "unlabeled_images.zip"
"""

IMG_SHAPE = (96,96,3)
SIZE = 96*96*3

DATA_DIR = '/content/gdrive/My Drive/stl10_binary'
TRAIN_DATA_PATH = '/content/gdrive/My Drive/stl10_binary/train_X.bin'
TRAIN_LABEL_PATH = '/content/gdrive/My Drive/stl10_binary/train_y.bin'

TEST_DATA_PATH = '/content/gdrive/My Drive/stl10_binary/test_X.bin'
TEST_LABEL_PATH = '/content/gdrive/My Drive/stl10_binary/test_y.bin'

#read_labels and read_all_images from Martin Tutek Github
def read_labels(path_to_labels):
 
    with open(path_to_labels, 'rb') as f:
        labels = np.fromfile(f, dtype=np.uint8)
        return labels


def read_all_images(path_to_data):
    

    with open(path_to_data, 'rb') as f:
        
        everything = np.fromfile(f, dtype=np.uint8)
        images = np.reshape(everything, (-1, 96, 96, 3))
        return images

import keras

x_train = read_all_images(TRAIN_DATA_PATH)
trainLabels = read_labels(TRAIN_LABEL_PATH)

x_test = read_all_images(TEST_DATA_PATH)
testLabels = read_labels(TEST_LABEL_PATH)

x_train = x_train/ 255
x_test = x_test/ 255
numLabels = keras.utils.to_categorical(trainLabels)
testLabels = keras.utils.to_categorical(testLabels)

print(len(trainLabels))
print(len(testLabels))

from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda
from keras.layers import Conv2D, Dropout, Activation, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras import backend as K
K.set_image_dim_ordering('tf')
IMAGE_HEIGHT = 96
IMAGE_WIDTH = 96

#!pip install keras==2.2.4

#from keras.applications.inception_v3 import InceptionV3
#base_model = InceptionV3(weights='imagenet', include_top=False, input_shape = (IMAGE_HEIGHT, IMAGE_WIDTH, 3))

#for layer in base_model.layers[:-12]:
  #  layer.trainable = False
 

def myNet():
    model = Sequential()
    #model.add(base_model)
    
    model.add(Conv2D(16,kernel_size=(3,3),activation='relu',input_shape=(IMAGE_HEIGHT,IMAGE_WIDTH,3)))
    model.add(Conv2D(16,kernel_size=(3,3),activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
    model.add(Dropout(0.5))
    
    model.add(Conv2D(16,kernel_size=(3,3),activation='relu'))
    model.add(Conv2D(16,kernel_size=(3,3),activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
    model.add(Dropout(0.5))
   
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.50))
    model.add(Dense(11, activation='softmax'))
   
    
    
    return model
    
model = myNet()

#Compile

base_learning_rate = 0.0001
model.compile(optimizer= 'adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

initial_epochs = 10
steps_per_epoch = 1000
validation_steps = 20
BATCH_SIZE = 256
SHUFFLE_BUFFER_SIZE = 1000

callbacks_list = None
history_one = model.fit(x_train, numLabels, validation_data=(x_test, testLabels), 
              epochs=initial_epochs, batch_size=BATCH_SIZE, callbacks=callbacks_list)

#Further Training
#Compile

model.compile(loss='categorical_crossentropy',
              optimizer = 'adam',
              metrics=['accuracy'])

#model.summary()

history = model.fit(x_train, numLabels, validation_data=(x_test, testLabels), 
              epochs=10, batch_size=BATCH_SIZE, callbacks=callbacks_list)
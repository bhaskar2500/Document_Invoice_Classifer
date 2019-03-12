import os
import pytesseract as pt
from flask import Flask,render_template,render_template_string,request,flash,Session,Response
from config import *
from PIL import Image as im
from PIL import ImageFile 
import numpy as np
import json
import base64
import io
##Keras
from keras.models import Model,Sequential
from keras.layers.recurrent import GRU
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image as ki
from keras import backend as K
from keras.layers.convolutional import Conv2D, MaxPooling2D ,Conv3D
from keras.layers import Input, Dense, Activation ,Flatten
from keras.layers import Reshape, Lambda 
from keras.layers.merge import add, concatenate
from keras.layers.normalization import BatchNormalization

app = Flask(__name__, instance_relative_config=True)
app.secret_key = config['secret_key']
app.config['SESSION_TYPE'] = config['SESSION_TYPE']

app.config['FILES_FOLDER'] = config['FILES_FOLDER']


    # a simple page that says hello
@app.route('/',methods = ['GET','POST'])
def uploaded_file():
        files= None
        K.clear_session()
        image = {}
        filename = save_uploaded_file()
        if filename is not None : 
            image = predict_image(os.path.join(app.config['FILES_FOLDER'],filename));
        else:
            image = None
        return render_template("index.html",image=image,showModal= True)
def predict_image(filename):
    size = (224,224)
    custom_vgg_model = create_model()
    custom_vgg_model.load_weights(os.path.join(app.config['FILES_FOLDER'],'DocumentClassifier.h5'))
    img = im.open(filename) 
    img = img.convert('RGB')
    img =img.resize(size,) 
    img_array = ki.img_to_array(img)    
    img_array = np.expand_dims(img_array,axis=0)
    prediction = custom_vgg_model.predict(img_array)
    prediction_output= {"type":"Invoice",} if prediction.argmax() else  {"type":"Other Document" }
    return prediction_output

def save_uploaded_file():
     # file ={"filename":''}
    if request.method =='POST':
        files = request.files
        if files : 
            file = files['file']
            print(file.filename)
            filename = file.filename
            file.save(os.path.join(app.config['FILES_FOLDER'],filename))
            print(filename,'***')
            return filename 
    return None
    #code to predict 
def create_model():
    image_input = Input(shape=(224, 224, 3))

    model = VGG16(input_tensor=image_input, include_top=True,weights='imagenet')

    last_layer = model.get_layer('block5_pool').output
    x= Flatten(name='flatten')(last_layer) 
    x= Dense(128,activation='relu',name='fc1')(x)
    x= Dense(128,activation='relu',name='fc2')(x)
    out = Dense(2, activation='softmax', name='output')(x)
    custom_vgg_model = Model(image_input, out)

    for layer in custom_vgg_model.layers[:-3]:
        layer.trainable = False

    custom_vgg_model.compile(loss='categorical_crossentropy',optimizer='rmsprop',metrics=['accuracy'])
    return custom_vgg_model

@app.route('/get_text', methods=['GET', 'POST'])
def get_text():
    text= None
    filename = request.form.get('filename')
    image = im.open(os.path.join('files',filename),'r')
    text = pt.image_to_string(image)
    print(text)
    return json.dumps({"text":text})


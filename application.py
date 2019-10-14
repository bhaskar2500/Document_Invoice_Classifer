import os
import pytesseract as pt
pt.pytesseract.tesseract_cmd = r"C:\Users\bhaskark847\AppData\Local\Tesseract-OCR\tesseract.exe"
from dbQueries import getExtractedData
from flask import Flask,render_template,render_template_string,request,flash,Response,jsonify
from config import *
from PIL import Image as im
import numpy as np
import json
import io
import base64
import datetime;
import pickle
from pdf2image import convert_from_path

##Keras
# from tensorflow.keras.models import Model,Sequential
# from keras.preprocessing import image as ki
# from tensorflow.keras import backend as K
# from tensorflow.keras.layers import Input, Dense, Activation ,Flatten,GlobalAveragePooling2D
    # from tensorflow.keras.applications import MobileNet
# from tensorflow.keras import regularizers

#Sentiment Keras imports
from keras.layers import Dense, Activation ,Flatten,GlobalAveragePooling2D,Input
from keras import regularizers
from keras.models import Model
from keras import backend as K
from keras.models import  load_model
from keras.applications import MobileNet
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing import image as ki

app = Flask(__name__, instance_relative_config=True)
app.secret_key = config['secret_key']
app.config['SESSION_TYPE'] = config['SESSION_TYPE']

app.config['FILES_FOLDER'] = config['FILES_FOLDER']
app.config['CONVERTED_FOLDER'] = config['CONVERTED_FOLDER']


@app.route('/',methods = ['GET','POST'])
def load_index():
    return render_template("index.html",)

    # a simple page that says hello
@app.route('/predictImage',methods = ['POST'])
def uploaded_file():
	try:
		files= None
		image = {}
		file=request.files.get('uploadedFile[]')
		filenames = save_uploaded_file()
        # if filenames is not None and filenames[0].endswith(".pdf"):
            # filenames[0] = filenames[0].replace('.pdf','.jpg')
		image = predict_image   (filenames[0]);
		# else:
		# 	image = None
		return jsonify(image)
	except Exception as ex:
		return jsonify({"type":"not completed "+str(ex)})
def convert_pdf_to_img(filenames):
    for file in filenames :
        if(file.endswith('.pdf')):
            pages = convert_from_path(os.path.join(app.config['FILES_FOLDER'],file), 500
            ,output_folder =os.path.join(app.config['CONVERTED_FOLDER'],file) )            

            #convert the file . 

def predict_image(filename):
    size = (224,224)
    K.clear_session()
    custom_vgg_model = create_model()
    custom_vgg_model.load_weights(os.path.join(app.config['FILES_FOLDER'],'OptimisedDocClassifier.h5'))
    img = im.open(filename) 
    img = img.convert('RGB')
    img =img.resize(size,) 
    img_array = ki.img_to_array(img)    
    img_array = np.expand_dims(img_array,axis=0)
    prediction = custom_vgg_model.predict(img_array)
    prediction_output= {"type":"Invoice",} if prediction.argmax() else  {"type":"Other Document" }
    K.clear_session()
    return prediction_output

def save_uploaded_file():
    filenames = []
    fileDataArr = []
    if request.method =='POST':
        files = request.files
        image = []
        print(files,'---')
        if files : 
            fileData = request.files.get('uploadedFile[]')
            fileDataArr.append(fileData)
            for file in fileDataArr:
                if file.filename.endswith('.pdf') :
                    file.save(os.path.join(app.config['FILES_FOLDER'],file.filename))
                    image = convert_from_path(os.path.join(app.config['FILES_FOLDER'],file.filename),500,output_folder = os.path.join(app.config['CONVERTED_FOLDER']),poppler_path='C:\\poppler-0.68.0\\bin',fmt='jpg',output_file=file.filename.replace('.pdf','.jpg'))
                if(file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.JPG')):
                    file.save(os.path.join(app.config['CONVERTED_FOLDER'],file.filename)) 
                if(len(image)>0):
                    filenames.append(image[0].filename)
                else:
                    filenames.append(os.path.join(app.config['CONVERTED_FOLDER'],file.filename))
            return filenames 
    return None
   # code to predict 
def create_model():
    K.clear_session()
    base_model=MobileNet(weights='imagenet',include_top=False) #imports the mobilenet model and discards the last 1000 neuron layer.
    x=base_model.output
    x=GlobalAveragePooling2D()(x)
    x= Dense(128,activation='relu',name='fc1')(x)
    x= Dense(128,activation='relu',name='fc2',kernel_regularizer=regularizers.l2(0.01))(x) #dense layer 3
    preds=Dense(2,activation='softmax')(x) #final layer with softmax activation
    custom_vgg_model = Model(inputs=base_model.input,outputs=preds)
    for layer in custom_vgg_model.layers[:-3]:
        layer.trainable=False
    for layer in custom_vgg_model.layers[-3:]:
        layer.trainable=True
    return custom_vgg_model

@app.route('/get_text', methods=['GET', 'POST'])
def get_text():
    text= None
    filenames = save_uploaded_file()
    print(filenames)
    for filename in filenames:
        print(filename)
        image = im.open(filename,'r')
        print(image)
        text = pt.image_to_string(image)
        getExtractedData(text)
        
    return json.dumps({"text":text})

@app.route('/predictSentiment',methods = ['POST'])
def predictSentiment():
    K.clear_session()
    labels  ={0:"Detractor",1:"Neutral",2:"Promoter"}
    with open(os.path.join(app.config['FILES_FOLDER'],'tokenizer.pickle'), 'rb') as handle:
        tokenizer = pickle.load(handle)
    model = load_model(os.path.join(app.config['FILES_FOLDER'],'SentimentModel.h5'))
    print(request.form)
    text_to_predict = request.form.get('sentimentText')
    text_to_predict = text_to_predict.split(' ')
   
    text_to_predict = tokenizer.texts_to_sequences([text_to_predict])
    text_to_predict = pad_sequences(text_to_predict,maxlen=200)
    prediction = model.predict(text_to_predict)
    print(prediction)
    predictedText   = labels[prediction.argmax()]  
    return json.dumps({"predictedText":predictedText,"score":str(prediction[0][prediction.argmax()])  })

def create_sentiment_model(vocab_size):
    embed_dim = 128
    lstm_out =196
    vocab_size = vocab_size
    model = Sequential()
    model.add(Embedding(vocab_size, embed_dim,input_length = 200))
    model.add(SpatialDropout1D(0.4))
    model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(3,activation='softmax'))
    model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
    return model

app.run(host= '0.0.0.0')
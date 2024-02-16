import flask
from flask import Flask, request, jsonify, make_response, render_template,json, Blueprint,flash
from .models import Para, Predicted, Status
from . import db

from re import X
import numpy as np
import pandas as pd
import pickle
import sklearn
import os
from datetime import datetime
from sklearn.model_selection import train_test_split

current_dir = os.path.dirname(os.path.realpath(__file__))
hydro = Blueprint('hydro', __name__)

#Dataset
test_data = pd.read_csv(current_dir+'/static/datasets/FinalDataset.csv')#retrieving csv file
para = test_data.drop(columns=['ph_s','wt_s','ec_s']) # actually also preprocessing

#preprocessing
x = para.drop(columns=['status'])
y = para['status']

#train test split function
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=91)

#Naive Bayes
with open (current_dir+'/NBmodel_pickle', 'rb') as f:
    NBmodel = pickle.load(f)


#predict response
nr_correct = (y_test == NBmodel.predict(x_test.values)).sum() #correct
nr_incorrect = y_test.size - nr_correct #incorrect
fraction_wrong = nr_incorrect / (nr_correct+nr_incorrect) #accuracy
nb_acc = (1-fraction_wrong)*100

#SVM
with open (current_dir+'/SVMmodel_pickle', 'rb') as f:
    SVMmodel = pickle.load(f)

#predict response
svm_correct = (y_test.values == SVMmodel.predict(x_test.values)).sum() #correct
svm_incorrect = y_test.size - svm_correct #incorrect
svm_fraction_wrong = svm_incorrect / (svm_correct+svm_incorrect) #accuracy
svm_acc = (1-svm_fraction_wrong)*100

#note to self: formating is always ph,wt,ec
#1= abnormal, 2 = below normal, 0 = normal
#in case of 102 -- ph = abnormal, wt = normal, ec = below normal


@hydro.route('/coll', methods=['GET', 'POST'])
def coll():
    ph=float(request.args['ph'])
    wt=float(request.args['wt'])
    ec=float(request.args['ec'])

    # offset
    

    ph_s = 0
    wt_s = 0
    ec_s = 0

    #for ph status
    if ph > 6.2:
        ph_s = 1
    elif ph < 5.5:
        ph_s = 2
    else:
        ph_s = 0
        
    #for wt status
    if wt > 22:
        wt_s = 1
    elif wt < 18:
        wt_s = 2
    else:
        wt_s = 0

    #for ec status
    if ec > 2.5:
        ec_s = 1
    elif ec < 1.2:
        ec_s = 2
    else:
        ec_s = 0


    def concat(ph_s, wt_s, ec_s):
        return int(f"{ph_s}{wt_s}{ec_s}")

    status = concat(ph_s, wt_s, ec_s)

    new_para = Para(ph=ph, ph_s=ph_s, wt=wt, wt_s=wt_s, ec=ec, ec_s=ec_s, status=status)
    db.session.add(new_para)
    db.session.commit()
    flash("Success", category='success')
    return "Yey"


@hydro.route('/pred', methods=['GET', 'POST'])
def main():
        ph=request.args['ph']
        wt=request.args['wt']
        ec=request.args['ec']
        tester_api= [[ph,wt,ec]]
        b = np.array(tester_api, dtype=float)
        NB = ",".join(map(str, NBmodel.predict(b)))
        SVM = ",".join(map(str, SVMmodel.predict(b)))
        # context = {
        #     "ph" : ph,
        #     "wt" : wt,
        #     "ec" : ec,
        #     "NB" : NB,
        #     "NB_acc" : nb_acc,
        #     "SVM" : SVM,
        #     "SVM_acc" : svm_acc
        # }
        # pred =  Predicted.query.filter_by(id=1).first()
        # compare_pred = Predicted.query.filter_by(id=2).first()

        # rows = Predicted.query.count()
        # if not rows < 2:
        #     ph_c = compare_pred.ph - pred.ph
        #     wt_c = compare_pred.wt - pred.wt
        #     ec_c = compare_pred.ec - pred.ec
        # else:
        #     pass



        # context = {
        #     "ph" : pred.ph,
        #     "wt" : pred.wt,
        #     "ec" : pred.ec,
        #     "NB" : pred.nb,
        #     "NB_acc" : nb_acc,
        #     "SVM" : pred.svm,
        #     "SVM_acc" : svm_acc,
        #     "phdiff" : ph_c,
        #     "wtdiff" : wt_c,
        #     "ecdiff" : ec_c,
        #     "date" : pred.date
        # }
        # req = request.get_json()

        # print(req)

        # res = jsonify(data)
        new_para = Predicted(ph=ph, wt=wt, ec=ec, nb=NB, svm=SVM)
        db.session.add(new_para)
        db.session.commit()

        flash("Success", category='success')
        # return render_template("predict.html", data=context)
        return "yes"
        # return res
        #render_template("pred.html", res=res)

@hydro.route('/')
def display():

    pred = Predicted.query.order_by(Predicted.id.desc()).first()
    compare_pred = Predicted.query.order_by(Predicted.id.desc()).offset(1).first()

    phchart = []
    wtchart = []
    ecchart = []
    time = []

    nbchart = []
    svmchart = []
    thetime = ""

    
    
    rows = Predicted.query.count()
    if rows < 14:
        i=rows-1
    else:
        i=13

    if not rows < 14:
        while i >= 0:
            phchart.append(Predicted.query.order_by(Predicted.id.desc()).offset(i).first().ph)
            wtchart.append(Predicted.query.order_by(Predicted.id.desc()).offset(i).first().wt)
            ecchart.append(Predicted.query.order_by(Predicted.id.desc()).offset(i).first().ec)
            nbchart.append(Predicted.query.order_by(Predicted.id.desc()).offset(i).first().nb)
            svmchart.append(Predicted.query.order_by(Predicted.id.desc()).offset(i).first().svm)

            thetime = str(Predicted.query.order_by(Predicted.id.desc()).offset(i).first().date).split()
            timesplit = str(thetime[1]).split(":")
            hour = timesplit[0]
            minute = timesplit[1]
            second = timesplit[2]

            if int(hour) > 12:
                answer = int(hour)-12
                hour = str(answer)
            else:
                pass

            time.append(hour+":"+minute+":"+second)
            i -= 1
    else:
        pass

    # ph_c = compare_pred.ph - pred.ph
    # wt_c = compare_pred.wt - pred.wt
    # ec_c = compare_pred.ec - pred.ec

    # nb = str(pred.nb)
    # svm = str(pred.svm)

    nbstat= Status.query.filter_by(status=pred.nb).first().recommend
    svmstat= Status.query.filter_by(status=pred.svm).first().recommend

    nbtitle= Status.query.filter_by(status=pred.nb).first().title
    svmtitle= Status.query.filter_by(status=pred.svm).first().title

    context = {
        "ph" : pred.ph,
        "wt" : pred.wt,
        "ec" : pred.ec,
        "NB" : pred.nb,
        "NB_acc" : nb_acc,
        "SVM" : pred.svm,
        "SVM_acc" : svm_acc,
        "phdiff" : compare_pred.ph,
        "wtdiff" : compare_pred.wt,
        "ecdiff" : compare_pred.ec,
        "date" : pred.date,
        "NB_stat" : nbstat,
        "SVM_stat" : svmstat,
        "NB_title" : nbtitle,
        "SVM_title" : svmtitle
    }


    

    barchart=[pred.ph, pred.ec, pred.wt]

    return render_template("predict.html", data=context, labels=time, phdata=phchart, wtdata=wtchart, ecdata=ecchart, barchart=barchart, nbchart=nbchart, svmchart=svmchart)
        

@hydro.route('/displaycoll')
def displaycoll():

    pred = Para.query.order_by(Para.id.desc()).first()
    # compare_pred = Predicted.query.order_by(Predicted.id.desc()).offset(1).first()

    id = []
    ph = []
    ph_s = []
    wt = []
    wt_s =[]
    ec = []
    ec_s = []
    status = []


    thetime = ""

    rows = Para.query.count()
    i=0

    if not rows < 14:
        while i <= 13:
            id.append(Para.query.order_by(Para.id.desc()).offset(i).first().id)
            ph.append(str(Para.query.order_by(Para.id.desc()).offset(i).first().ph))
            ph_s.append(Para.query.order_by(Para.id.desc()).offset(i).first().ph_s)
            wt.append(str(Para.query.order_by(Para.id.desc()).offset(i).first().wt))
            wt_s.append(Para.query.order_by(Para.id.desc()).offset(i).first().wt_s)
            ec.append(str(Para.query.order_by(Para.id.desc()).offset(i).first().ec))
            ec_s.append(Para.query.order_by(Para.id.desc()).offset(i).first().ec_s)
            status.append(Para.query.order_by(Para.id.desc()).offset(i).first().status)
            i += 1
    else:
        pass

    content = list(zip(id,ph,ph_s,wt,wt_s,ec,ec_s,status))

    return render_template("display.html", data = content)

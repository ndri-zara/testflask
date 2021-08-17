from flask import Flask, render_template, url_for, request
import pandas as pd
from pickle import load
import numpy as np
import joblib
from flask_mysqldb import MySQL, MySQLdb
import pickle




app = Flask(__name__)

model=pickle.load(open('models/ok.plk','rb')) #model = joblib.load('ok.plk', 'rb') remarque importante à ce niveau c'est sa place di vous le déplacez vous aurez une erreur 

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='carte_bancaire'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql= MySQL(app)

@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/second')
def second(): 
    df = pd.read_csv("data/bien.csv" , sep=',')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    result = cur.execute("SELECT * FROM bien450 ORDER BY preds")
    employee = cur.fetchall()
    return render_template('table.html', employee = employee)

@app.route('/quatrième')
def own_prediction():
    
    return render_template('formulaire.html')

@app.route('/six')
def six():
    
    return render_template('manip.html')

@app.route('/predict',methods=['POST'])
def predict():

        
    âge = float(request.form['âge']) #très important float,str,int pour spécifier
    étude = float(request.form['étude'])
    revenu = float(request.form['revenu'])
    catégorie = float(request.form['catégorie'])
    utilisation = float(request.form['utilisation'])
    limite = float(request.form['limite'])
    genre = float(request.form['genre'])

    vect = np.array([[âge, étude, revenu, catégorie, limite, utilisation,  genre]])

    my_prediction = model.predict(vect)
   
       
    return render_template("resultat.html", my_prediction=my_prediction, âge=âge, étude=étude, revenu=revenu, catégorie=catégorie, limite=limite, utilisation=utilisation,  genre=genre)
    


@app.route('/troisième')
def troisième():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    result = cur.execute("SELECT * FROM bien450 ORDER BY rand() LIMIT 10")
    employe = cur.fetchall()
    return render_template('predit_aleatoirement.html', employe = employe)

@app.route('/cinq')
def cinq():
    
    return render_template('charger.html')
   


@app.route("/ajaxfile",methods=["POST","GET"])
def ajaxfile():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    result = cur.execute("SELECT * FROM bien450 ORDER BY preds")
    employee = cur.fetchall()
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw'] 
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
 
            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from bien450")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords) 
 
            ## Total number of records with filtering
            likeString = "%" + searchValue +"%"
            cursor.execute("SELECT count(*) as allcount from bien450 WHERE preds LIKE %s OR Attrition_Flag LIKE %s OR Gender LIKE %s", (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter) 
 
            ## Fetch records
            if searchValue=='':
                cursor.execute("SELECT * FROM bien450 ORDER BY preds asc limit %s, %s;", (row, rowperpage))
                employeelist = cursor.fetchall()
            else:        
                cursor.execute("SELECT * FROM bien450 WHERE preds LIKE %s OR position LIKE %s OR office LIKE %s limit %s, %s;", (likeString, likeString, likeString, row, rowperpage))
                employeelist = cursor.fetchall()
 
            data = []
            for row in employeelist:
                data.append({
                    'preds': row['preds'],
                    'Attrition_Flag': row['Attrition_Flag'],
                    'Customer_Age': row['Customer_Age'],
                    'Education_Level': row['Education_Level'],
                    'Income_Category': row['Income_Category'],
                    'Card_Category': row['Card_Category'],
                    'Credit_Limit': row['Credit_Limit'],
                    'Avg_Utilization_Ratio': row['Avg_Utilization_Ratio'],
                    'Gender': row['Gender'],
                })
 
            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
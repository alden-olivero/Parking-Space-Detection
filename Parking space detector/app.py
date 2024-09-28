
from flask import Flask, render_template, request, session
import cv2
import pickle
import cvzone
import numpy as np
import pymysql  # Use pymysql instead of ibm_db
import re
import matplotlib.pyplot as plt
app = Flask(__name__)
app.secret_key = 'a'
conn = pymysql.connect(host="localhost", user="root", password="", database="parking", port=3306)
print("connected")

@app.route('/')
def project():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/model')
def model():
    return render_template('model.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/aboutus.html')
def aboutus():
    return render_template('aboutus.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')
@app.route("/signup", methods=['POST', 'GET'])
def signup1():
    msg = ''
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        cursor = conn.cursor()
        insert_sql = "INSERT INTO REGISTER (NAME, EMAIL, PASSWORD) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (name, email, password))
        conn.commit()
        msg = "You have successfully registered!"
    return render_template('login.html', msg=msg)

@app.route("/login", methods=['POST', 'GET'])
def login1():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor = conn.cursor()
        sql = "SELECT * FROM REGISTER WHERE EMAIL=%s AND PASSWORD=%s"
        cursor.execute(sql, (email, password))
        account = cursor.fetchone()
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account[0]  # Assuming the first column is the user ID
            session['email'] = account[1]  # Assuming the second column is the email
            return render_template('model.html')
        else:
            msg = "Incorrect Email/password"
            return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')


@app.route('/modelq')
def liv_pred():
    # Video feed
    cap = cv2.VideoCapture('carParkingInput.mp4')
    with open('parkingSlotPosition', 'rb') as f:
        posList = pickle.load(f)
    width, height = 107, 48
    def checkParkingSpace(imgPro):
        spaceCounter = 0
        for pos in posList:
            x, y = pos
            imgCrop = imgPro[y:y + height, x:x + width]
            count = cv2.countNonZero(imgCrop)
            if count < 900:
                color = (0, 255, 0)
                thickness = 5
                spaceCounter += 1
            else:
                color = (0, 0, 255)
                thickness = 2
            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3, thickness=5, offset=20,
                       colorR=(0, 200, 0))
        


    while True:
        success, img = cap.read()
        if not success:
            break

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                             25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
        checkParkingSpace(imgDilate)

        # Display the image using matplotlib
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.pause(0.1)
        
        if plt.waitforbuttonpress(timeout=0.1):  # Adjust timeout as needed
            break
    plt.close()
    cap.release()
    

if __name__ == "__main__":
    app.run(debug=True)
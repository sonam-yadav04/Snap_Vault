import base64
from flask import Flask, render_template, redirect, request, url_for,send_file
from io import  BytesIO
import mysql.connector

app = Flask(__name__)
def get_connection():
  return mysql.connector.connect(
      host ="localhost",
      user = "root",
      password = "Sonam123",
      database = "uploaddb"
     )


@app.route("/",methods=['GET','POST'])
def home():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("select id ,filename ,data from uploads")
    files = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
     # converting binary file into base64 formate
    file_list = []
    for file in files:
        id, file_name, data = file
        if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            image_data = base64.b64encode(data).decode('utf-8')
            file_list.append({"id": id, "filename": file_name, "image": image_data})
        else:
            file_list.append({"id": id, "filename": file_name, "image": None})

    return render_template("home.html", files=file_list)



@app.route("/upload",methods=['GET','POST'])
def upload():
    if request.method == 'POST':
       file = request.files['file']
       if file:
            conn = get_connection()
            cur = conn.cursor()
            sql = "insert into uploads(filename,data) values(%s,%s)"
            cur.execute(sql, (file.filename, file.read()))
            conn.commit()
            cur.close()
            conn.close()
       return redirect(url_for('home'))
    return render_template("upload.html")


@app.route("/download/<int:file_id>")
def download(file_id):

    return render_template("download.html", file_id=file_id)

@app.route("/start-download/<int:file_id>")
def start_download(file_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, data FROM uploads WHERE id = %s", (file_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        filename, data = result
        send_file(BytesIO(data), download_name=filename, as_attachment=True)
        return redirect(url_for('home'))
    else:
        return "File not found", 404



if __name__=='__main__':
    app.run(debug = True)
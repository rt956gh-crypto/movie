@app.route("/", methods=["GET", "POST"])
def index():
    # 當使用者一進來網頁時，顯示 input.html 表單
    return render_template("input.html")
from flask import Flask, render_template, request
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# 判斷是在 Vercel 還是本地，讀取 Firebase 金鑰 
if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/", methods=["POST", "GET"])
@app.route("/searchQ", methods=["POST", "GET"])
def searchQ():
    if request.method == "POST":
        movie_title = request.form["MovieTitle"]
        info = ""
        # 從 Firestore 讀取電影資料 
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        
        for doc in docs:
            data = doc.to_dict()
            if movie_title in data["title"]:
                # 顯示片名、海報、介紹頁超鏈結 
                info += f"<h3>片名：{data['title']}</h3>"
                info += f"<img src='{data['picture']}' width='200'><br>"
                info += f"<a href='{data['hyperlink']}' target='_blank'>影片介紹頁面</a><br>"
                info += f"上映日期：{data['showDate']}<br><br><hr>"
        
        if not info:
            info = "抱歉，查無相關電影資料。"
        return info + "<br><a href='/'>返回搜尋</a>"
    else:
        # 顯示輸入表單 
        return render_template("input.html")
# 刪除或註解掉原本的 app.run()
# app.run() 

# 確保 Vercel 可以抓到 app 這個變數
if __name__ == "__main__":
    app.run(debug=True)

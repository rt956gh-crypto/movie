from flask import Flask, render_template, request
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# 1. Firebase 初始化
if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 這是給 Vercel 環境變數使用的邏輯
    firebase_config = os.getenv('FIREBASE_CONFIG')
    if firebase_config:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
    else:
        # 如果既沒有檔案也沒有環境變數，這裡會報錯，方便你除錯
        raise ValueError("找不到 Firebase 金鑰設定")

# 避免重複初始化
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. 路由設定
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
        # 顯示搜尋表單 
        return render_template("input.html")

# 3. 啟動設定 (Vercel 會自動抓取 app 物件，這段主要用於本地測試)
if __name__ == "__main__":
    app.run(debug=True)

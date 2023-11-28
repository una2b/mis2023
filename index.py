import requests
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>毛姿云Python網頁11/28</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=毛姿云>傳送使用者暱稱</a><br>"
    homepage += "<a href=/about>姿云簡介網頁</a><br>"
    homepage += "<br><a href=/read>人選之人演員查詢</a><br>"
    homepage += "<br><a href=/books>精選圖書列表</a><br>"
    homepage += "<br><a href=/query>圖書查詢</a><br>"
    homepage += "<a href=/account>網頁表單</a><br>"
    homepage += "<a href=/spider>網路爬蟲抓取子青老師課程</a><br>"
    homepage += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<a href=/searchQ>查詢開眼電影即將上映影片</a><br>"
    return homepage


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html",datetime = str(now))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    user = request.values.get("nick")
    return render_template("welcome.html", name=user)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd
        return result
    else:
        return render_template("account.html")

@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("人選之人-造浪者")
    docs = collection_ref.get()
    for doc in docs:
        Result += "文件內容 : {}".format(doc.to_dict()) + "<br>"
        return Result

@app.route("/books")
def books():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("圖書精選")
    docs = collection_ref.get()
    for doc in docs:
        bk = doc.to_dict()
        Result += "書名:<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
        Result += "作品:" + bk["author"] + "<br>"
        Result += str(bk["anniversary"]) + "週年紀念版<br>"
        Result +="<img src =" + bk["cover"] + "> </img><br><br><br>"
    return Result

@app.route("/query",methods=["GET","POST"])
def query():
    if request.methods == "POST":
        keyword = request.form["keyword"]
        result = "您輸入的關鍵字是:" + keyword

        Result = ""
        db = firestore.client()
        collection_ref = db.collection("圖書精選")
        docs = collection_ref.get()
        for doc in docs:
            bk = doc.to_dict()
            if keyword in bk["title"]:
                Result += "書名:<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
                Result += "作品:" + bk["author"] + "<br>"
                Result += str(bk["anniversary"]) + "週年紀念版<br>"
                Result +="<img src =" + bk["cover"] + "> </img><br><br><br>"
        return Result
    else:
        return render_template("searchbk.html")

@app.route("/spider")
def spider():
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box")
    info  = ""
    for x in result:
        info += "<a href=" + x.find("a").get("href") + ">" + x.text + "<br>"
        info += x.find("a").get("href") + "<br><br>"

    return info

@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
}

        db = firestore.client()
        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)    
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 



@app.route("/find")
def find():
    info = ""
    db = firestore.client()  
    docs = db.collection("電影").get() 
    for doc in docs:
        if "飛鴨" in doc.to_dict()["title"]:
            info += "片名：" + doc.to_dict()["title"] + "<br>" 
            info += "海報：" + doc.to_dict()["picture"] + "<br>"
            info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
            info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
            info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"           
    return info

@app.route("/searchQ", methods=["POST","GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()     
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: 
                info += "片名：" + doc.to_dict()["title"] + "<br>" 
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"           
        return info
    else:  
        return render_template("input.html")





if __name__ == "__main__":
    app.run(debug=True)

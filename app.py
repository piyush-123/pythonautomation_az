from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin
from flask_sqlalchemy import SQLAlchemy

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import mysql.connector as connection
import time
from selenium import webdriver
import base64
import pymongo
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fjrviynkaqwkrr:cc28dd22119ff4818b4660ffcb2c422c15c39a72b89b5361a17deaf6dea13436@ec2-54-204-241-136.compute-1.amazonaws.com:5432/d360b6ar5bv5os'
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

#class Youtube(db.Model):
#    __tablename__ = 'youtubers'
#    id = db.Column(db.Integer,primary_key=True)
#    name = db.Column(db.String(40))
#    video_url = db.Column(db.String(100))
#    video_likes = db.Column(db.String(50))
#    video_comments = db.Column(db.String(50))

#    def __init__(self,name,video_url,video_likes,video_comments):
#        self.name = name
#        self.video_url = video_url
#        self.video_likes = video_likes
#        self.video_comments = video_comments

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("window-size=1400,900")


@app.route('/',methods=['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/analyse',methods=['POST','GET'])
@cross_origin()
def analyse_link():
    if request.method == 'POST':
        try:
            searchUrl = request.form['youtubelink'].replace(" ","")
            Driver = 'chromedriver.exe'
            image_urls = []
            title_names = []
            video_urls = []

            count = 0

            name = searchUrl.split('/')[4]
            wd = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)
            #wd = webdriver.Chrome(executable_path=Driver)
            wd.get(searchUrl)
            wd.maximize_window()
            time.sleep(1)

            def f1():
                w_count = 0
                items = wd.find_elements("xpath", "//*[@id='items']/ytd-grid-video-renderer")

                for i in range(1,len(items)+1):
                    query1 = f"//*[@id='items']/ytd-grid-video-renderer[{i}]/div[1]/ytd-thumbnail/a/yt-img-shadow/img"
                    query2 = f"//*[@id='items']/ytd-grid-video-renderer[{i}]/div[1]/div[1]/div[1]/h3/a"
                    shorts_query = f"//*[@id='items']/ytd-grid-video-renderer[{i}]/div[1]/ytd-thumbnail/a/div/ytd-thumbnail-overlay-time-status-renderer/span"
                    try:
                        check_short = wd.find_element("xpath", shorts_query).get_attribute('aria-label')
                        if check_short == "Shorts":
                            ignore = True
                        else:
                            ignore = False
                    except:
                        ignore = False
                    if not ignore:
                        thumbnail = wd.find_element("xpath", query1).get_attribute('src')
                        video_link = wd.find_element("xpath", query2).get_attribute('href')
                        title = wd.find_element("xpath", query2).get_attribute('title')

                        if thumbnail and thumbnail not in image_urls:
                            image_urls.append(thumbnail)
                            title_names.append(title)
                            video_urls.append(video_link)
                            w_count = w_count + 1

                return w_count

            while count < 30 :
                temp = f1()
                count = count + temp
                wd.execute_script("window.scrollBy(0, 500)"," ")
                time.sleep(1)

            reviews = []
            for i in range(len(image_urls)):
                reviews.append({"Video_URL":video_urls[i],"Video_Title":title_names[i],"Video_Thumbnail":image_urls[i]})



            wd.close()
            return render_template('results.html',reviews=reviews[0:(len(reviews)-1)],name=name)
        except Exception as e:
            print(e)
            return "error"

@app.route('/details',methods=['POST'])
@cross_origin()
def detail_link():
    if request.method == 'POST':
        try:
            searchUrl = request.form['video_dt'].replace(" ","")
            name = request.form['video_name']
            thumbnail = request.form['video_thumbnail']
            Driver = 'chromedriver.exe'


            commenter=[]
            commenter_desc=[]
            reply_num = []

            wd = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
            #wd = webdriver.Chrome(executable_path=Driver)
            wd.get(searchUrl)
            wd.maximize_window()
            #wd.execute_script("window.focus();")
            time.sleep(1)
            wait = WebDriverWait(wd, 10)

            likes_result = 0


            def f2():

                w_count = 0
                reply_count = 0
                items = wd.find_elements("xpath", "//*[@id='contents']/ytd-comment-thread-renderer")
                for j in range(1, len(items) + 1):
                    query1 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/ytd-comment-renderer/div[3]/div[2]/div[1]/div[2]/h3/a/span"
                    query2 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/ytd-comment-renderer/div[3]/div[2]/div[2]/ytd-expander/div/yt-formatted-string/span"
                    try:
                        comment_name = wd.find_element("xpath", query1).text
                        comment_desc = wd.find_element("xpath", query2).text
                        try:
                            query3 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/div/ytd-comment-replies-renderer/div/div[1]/div[1]/ytd-button-renderer/a/tp-yt-paper-button/yt-formatted-string"
                            replies = wd.find_element("xpath", query3).text
                            if replies:
                                reply_count = int(str(replies).split(' ')[0])


                        except:

                            reply_count = 0

                    except Exception as e:
                        comment_name = None
                        comment_desc = None

                    if not comment_desc:
                        query1 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/ytd-comment-renderer/div[3]/div[2]/div[1]/div[2]/h3/a/span"
                        query2 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/ytd-comment-renderer/div[3]/div[2]/div[2]/ytd-expander/div/yt-formatted-string"
                        try:

                            comment_name = wd.find_element("xpath", query1).text
                            comment_desc = wd.find_element("xpath", query2).text
                            try:
                                query3 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/div/ytd-comment-replies-renderer/div/div[1]/div[1]/ytd-button-renderer/a/tp-yt-paper-button/yt-formatted-string"
                                replies = wd.find_element("xpath", query3).text

                                if replies:
                                    reply_count = int(str(replies).split(' ')[0])



                            except:

                                reply_count = 0

                        except Exception as e:
                            comment_name = None
                            comment_desc = None

                    if comment_desc:
                        if comment_desc not in commenter_desc:

                            commenter.append(comment_name)
                            commenter_desc.append(comment_desc)
                            reply_num.append(reply_count)
                            w_count = w_count + 1 + reply_count
                        else:
                            w_count = w_count + 1 + reply_count

                return w_count

            #likes_result = wait.until(EC.presence_of_element_located((By.XPATH,
            #                                                               "//*[@id='top-level-buttons-computed']/ytd-toggle-button-renderer/a/yt-formatted-string"))).text
            timer = 0

            while True:
                try:

                    likes_check = wd.find_element("xpath",
                                           "//*[@id='top-level-buttons-computed']/ytd-toggle-button-renderer/a/yt-formatted-string")
                    likes_result = likes_check.text

                    break
                except:
                    if timer < 10:

                        wd.execute_script("window.scrollBy(0, 300)", " ")
                        timer = timer + 1
                    else:
                        break



            wd.execute_script("window.scrollBy(0, 200)", " ")
            z = 1
            time.sleep(1)
            comments_num = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                      "//*[@id='count']/yt-formatted-string/span[1]"))).text




            total = 0
            process = True

            while process:
                item_count = f2()
                total = total + item_count


                if total < int(comments_num):
                    wd.execute_script("window.scrollBy(0, 300)", " ")
                    time.sleep(1)
                else:
                    process = False
            reviews = []


            for i in range(0,len(commenter)):

                reviews.append(
                    {"Commenter Name": commenter[i], "Comments": commenter_desc[i],"Reply_cnt":reply_num[i]})
            wd.close()
#            youtuber = Youtube(name,searchUrl,likes_result,comments_num)
#            db.session.add(youtuber)
#            db.session.commit()
#            client = pymongo.MongoClient(
#                "mongodb+srv://piyush1304:System909@cluster0.gocvn.mongodb.net/?retryWrites=true&w=majority")

#            db_mongo = client['webscrapping']
#            coll = db_mongo['youtubers']
#            final_comment_details = {}
#            for m in range(len(commenter)):
#
#                video_title = searchUrl
                #video_src = base64.b64encode(image_urls[m].encode('ascii'))
                #for k in range(len(final_comments_name[m])):
#                video_commenter = commenter[m]
#                video_comment = commenter_desc[m]
#                video_comment_detail = {
#                        "commenter": video_commenter,
#                        "comments": video_comment
#                    }
#                final_comment_details[str(m)] = video_comment_detail

#            my_dict = {
#                    "Title": video_title,
#                    "Thumbnail" : base64.b64encode(thumbnail.encode('ascii')),
#                    "Comments": final_comment_details
#                }
#            coll.insert_one(my_dict)

            return render_template('details.html',reviews=reviews,url=searchUrl,likes=likes_result,comment_num=comments_num,name=name)
        except Exception as e:
            print(e)
            return "error in details"
if __name__ == '__main__':
    app.run()


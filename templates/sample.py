from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin

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

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")


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
            likes_result = []
            comments_count = []
            commenter=[]
            commenter_desc=[]
            final_comments_name = []
            final_comments_desc = []
            number_items = 0
            count = 0


            #wd = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)
            wd = webdriver.Chrome(executable_path=Driver)
            wd.get(searchUrl)
            #youtuber_name = searchUrl.split('/')[4]
            #print(youtuber_name)
            wd.maximize_window()
            wd.execute_script("window.focus();")
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

            while count < 5 :
                temp = f1()
                count = count + temp
                wd.execute_script("window.scrollBy(0, 500)"," ")
                time.sleep(1)
            print('reached here1')
            wait = WebDriverWait(wd, 15)
            print('reached here2')
            def f2():
                print("inside f2")
                w_count = 0
                reply_count = 0
                items = wd.find_elements("xpath", "//*[@id='contents']/ytd-comment-thread-renderer")
                for j in range(1,len(items)+1):
                    query1 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/ytd-comment-renderer/div[3]/div[2]/div[1]/div[2]/h3/a/span"
                    query2 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/ytd-comment-renderer/div[3]/div[2]/div[2]/ytd-expander/div/yt-formatted-string/span"
                    try:
                        comment_name = wd.find_element("xpath", query1).text
                        comment_desc = wd.find_element("xpath", query2).text
                        try:
                            query3 = f"//*[@id='contents']/ytd-comment-thread-renderer[{j}]/div/ytd-comment-replies-renderer/div/div[1]/div[1]/ytd-button-renderer/a/tp-yt-paper-button/yt-formatted-string"
                            replies = wd.find_element("xpath",query3).text
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
                            w_count = w_count + 1 + reply_count
                        else:
                            w_count = w_count + 1 + reply_count


                return w_count

            for i in video_urls:
                print(i)
                wd.get(i)
                wd.maximize_window()
                wd.execute_script("window.focus();")
                likes_result.append(wait.until(EC.presence_of_element_located((By.XPATH,
                                                                               "//*[@id='top-level-buttons-computed']/ytd-toggle-button-renderer/a/yt-formatted-string"))).text)

                print("reached here 4")
                wd.execute_script("window.scrollBy(0, 500)", " ")
                z = 1
                time.sleep(1)
                comments_num = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                                 "//*[@id='count']/yt-formatted-string/span[1]"))).text
                comments_count.append(comments_num)
                print("reached here 5")
                total = 0
                process = True
                print(comments_count)
                print('reached here3')
                while process:
                    item_count = f2()
                    total = total + item_count
                    if total < int(comments_num) :
                        wd.execute_script("window.scrollBy(0, 500)", " ")
                        time.sleep(1)
                    else:
                        process = False
                final_comments_name.append(commenter)
                final_comments_desc.append(commenter_desc)
                commenter = []
                commenter_desc = []

            print('saving now')
            my_db = connection.connect(host="localhost", user="root", passwd="root")
            cursor = my_db.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS webscraping")
            cursor.execute("Use webscraping")
            cursor.execute("CREATE Table IF NOT EXISTS youtubers(Youtuber_Name Varchar(50),Video_title varchar(100),Video_Thumbnail_link varchar(200),Video_url varchar(100),video_likes varchar(30),video_number_of_comments varchar(30))")
            for i in range(len(title_names)):
            #for i in range(2):
                Youtuber_Name = "Telusko"
                Video_title = title_names[i]
                Video_Thumbnail_link = str(image_urls[i])
                Video_url = str(video_urls[i])
                video_likes = likes_result[i]
                video_number_of_cmnts = comments_count[i]


                sql_query = "insert into youtubers(Youtuber_Name,Video_title,Video_Thumbnail_link,Video_url,video_likes,video_number_of_comments) values(%s,%s,%s,%s,%s,%s)"
                sql_data = (Youtuber_Name,Video_title,Video_Thumbnail_link,Video_url,video_likes,video_number_of_cmnts)

                try:
                    cursor.execute(sql_query,sql_data)
                    my_db.commit()

                except Exception as e:
                    print(e)
                    return "error occureed in sql"

            client = pymongo.MongoClient(
                "mongodb+srv://piyush1304:System909@cluster0.gocvn.mongodb.net/?retryWrites=true&w=majority")

            db_mongo = client['webscrapping']
            coll = db_mongo['youtubers']

            for m in range(len(title_names)):
                final_comment_details = {}

                video_title = title_names[m]
                video_src = base64.b64encode(image_urls[m].encode('ascii'))
                for k in range(len(final_comments_name[m])):
                    video_commenter = final_comments_name[m][k]
                    video_comment = final_comments_desc[m][k]
                    video_comment_detail = {
                        "commenter":video_commenter,
                        "comments" : video_comment
                    }
                    final_comment_details[str(k)] = video_comment_detail

                my_dict = {
                    "Title":video_title,
                    "Thumbnail_encoded":video_src,
                    "Comments": final_comment_details
                            }
                coll.insert_one(my_dict)



            return "Record are inserted in SQL and mongo"
        except Exception as e:
            print(e)
            return "error"


if __name__ == '__main__':
    app.run()


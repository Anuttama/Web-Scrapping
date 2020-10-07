# doing necessary imports

from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import matplotlib.pyplot as plt
import os
import traceback

app = Flask(__name__)  # initialising the flask app with the name 'app'
#home page redirection
@app.route('/home',methods=['GET'])
@cross_origin()
def homePage():
	return render_template("index.html")

#review page
@app.route('/review',methods=['POST','GET']) # route with allowed methods as POST and GET
@cross_origin()
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","") # obtaining the search string entered in the form
        try:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString # preparing the URL to search the product on flipkart
            uClient = uReq(flipkart_url) # requesting the webpage from the internet
            flipkartPage = uClient.read() # reading the webpage
            uClient.close() # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser") # parsing the webpage as HTML
            flipkart_baseurl = "https://www.flipkart.com"
            bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"}) # seacrhing for appropriate tag to redirect to the product link
            del bigboxes[0:3]
            box = bigboxes[0]
            #for box in bigboxes[:3]:
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] # extracting the actual product link
            #productName = box.div.div.div.a.img['alt']
            #print(productName)
            prodRes = requests.get(productLink) # getting the product page from server
            prod_html = bs(prodRes.text, "html.parser") # parsing the product page as HTML
            commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"}) # finding the HTML section containing the customer comments
            reviews = [] # initializing an empty list for reviews
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'
                #fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                        "Comment": custComment} # saving that detail to a dictionary

                reviews.append(mydict) #  appending the comments to the review list

            df = pd.DataFrame(reviews)
            save_wordcloud(df,searchString)
            return render_template('results.html', reviews=reviews) # showing the review to the user
        except:
            traceback.print_exc()
            #return 'something is wrong'
            return render_template('noresultfound.html')
    else:
        return render_template('index.html')

def save_wordcloud(df,searchString):
    comments = df["Comment"].values
    wc = WordCloud(width=1355, height=565, background_color='black', stopwords=STOPWORDS).generate(str(comments))
    image_path = os.path.join("static", "IMG_FOLDER", searchString + '.jpg')
    existingwordcloudimage()
    wc.to_file(image_path)

def existingwordcloudimage():
    if os.listdir("static/IMG_FOLDER") != list():
        files = os.listdir("static/IMG_FOLDER")
        for file in files:
            os.remove(os.path.join("static/IMG_FOLDER", file))

#wordcloud page
@app.route('/show')
@cross_origin()
def wordcloudPage():
    try:
        imageFile = os.listdir("static/IMG_FOLDER")[0]
        return render_template('wordcloud.html',imageFile = imageFile )
    except:
        traceback.print_exc()
        return 'something is wrong'

if __name__ == "__main__":
    app.run(port=8001) # running the app on the local machine on port 8000
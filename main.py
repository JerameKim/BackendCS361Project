from fastapi import FastAPI
from bs4 import BeautifulSoup
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import requests
import re
import uvicorn 

# start fastapi
app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Abstract(BaseModel): 
    text: str

class my_citation(object): 
    # link: str
    # text: str
    # id: str
    def __init__(self, link, text, id):
        self.link = link
        # gives all the text of the citation, stuff in quotes is the linked portion 
        # if nothing in quotes, whole thing is linkeo
        self.text = text
        self.id = id
class my_image(object): 
    # src: str
    # caption: str
    # id: str
    def __init__(self, src, caption,id):
        self.src = src
        self.caption = caption
        # 1 for thumbnail photo, greater than 1 for all other
        self.id = id
class my_category(object): 
    # link: str
    # text: str
    def __init__(self, link, text): 
        self.link = link 
        self.text = text
class my_chapter(object): 
    def __init__(self, link, text): 
        self.link = link 
        self.text = text
# endpoints 
# get request 
# fastAPI will automatically expect something that is an "abstract" to be in the body of the request
@app.get('/abstract/{lang}/{tag}')
def get_abstract(lang: str, tag: str): 

    languageURL = "https://en.wikipedia.org/wiki/"
    
    # Defaults to english if no language specified
    if(lang == "fr"): 
        languageURL = "https://fr.wikipedia.org/wiki/"
    if(lang == "it"): 
        languageURL = "https://it.wikipedia.org/wiki/"
    if(lang == "es"): 
        languageURL = "https://es.wikipedia.org/wiki/"
    if(lang == "ru"): 
        languageURL = "https://ru.wikipedia.org/wiki/"

    url = languageURL + tag
    html = requests.get(url) 
    html_text = "none"
    if(html.status_code==200): 
        html_text = requests.get(url).text
        
    else: 
        print(f"Failed get request from webpage with code {html.status_code}")
        return "Could not reach Wikipedia page.  Either the page does not exist or Wikipedia is currently unreachable."
        # exit(0)

    # format the text in lxml format 
    soup = BeautifulSoup(html_text, "lxml")

    try: 
        # gets all text content from page
        content = soup.find('div', class_ ='mw-parser-output')

        # gets all top level 'p' tags, which holds all the text
        paragraphs = content.find_all('p', recursive=False)
        
        for i in range(3): 
            # get the first paragraph tag that has content, this is usually the abstract
            if(len(paragraphs[i]) > 1): 
                firstParagraph = paragraphs[i].get_text()
                break

        return firstParagraph

    except: 
        return ""

@app.get('/text/{lang}/{tag}')
def get_main_text(lang: str, tag: str): 

    languageURL = "https://en.wikipedia.org/wiki/"
    
    # Defaults to english if no language specified
    if(lang == "fr"): 
        languageURL = "https://fr.wikipedia.org/wiki/"
    if(lang == "it"): 
        languageURL = "https://it.wikipedia.org/wiki/"
    if(lang == "es"): 
        languageURL = "https://es.wikipedia.org/wiki/"
    if(lang == "ru"): 
        languageURL = "https://ru.wikipedia.org/wiki/"

    url = languageURL + tag
    html = requests.get(url) 
    html_text = "none"
    if(html.status_code==200): 
        html_text = requests.get(url).text
    else: 
        print(f"Failed get request from webpage with code {html.status_code}")
        return "Could not reach Wikipedia page.  Either the page does not exist or Wikipedia is currently unreachable."
        # exit(0)
    
    # format the text in lxml format 
    soup = BeautifulSoup(html_text, "lxml")

    try: 
        # gets all text content from page
        content = soup.find('div', class_ ='mw-parser-output')

        # gets all top level 'p' tags, which holds all the text
        # paragraphs = content.find_all('p', recursive=False)
        paragraphs = content.find_all('p')

        # used to help remove brackets and their contents (regex)
        pattern = r'\[[^\]]*\]'
        for i in range(len(paragraphs)): 
            # removes HTML tags
            paragraphs[i] = paragraphs[i].get_text()
            # removes brackets and their contents 
            paragraphs[i] = re.sub(pattern, '', paragraphs[i])
            
        # remove any empty lines
        while("" in paragraphs):
            paragraphs.remove("")

        return paragraphs

    # no text can be found from paragraphs
    except: 
        return []

@app.get('/citations/{lang}/{tag}')
# gets the citations in a citaitons array obj
def get_citations(lang: str, tag: str): 

    languageURL = "https://en.wikipedia.org/wiki/"
    
    # Defaults to english if no language specified
    if(lang == "fr"): 
        languageURL = "https://fr.wikipedia.org/wiki/"
    if(lang == "it"): 
        languageURL = "https://it.wikipedia.org/wiki/"
    if(lang == "es"): 
        languageURL = "https://es.wikipedia.org/wiki/"
    if(lang == "ru"): 
        languageURL = "https://ru.wikipedia.org/wiki/"

    url = languageURL + tag
    html = requests.get(url) 
    html_text = "none"
    if(html.status_code==200): 
        html_text = requests.get(url).text
    else: 
        print(f"Failed get request from webpage with code {html.status_code}")
        return "Could not reach Wikipedia page.  Either the page does not exist or Wikipedia is currently unreachable."
        # exit(0)
    
    # format the text in lxml format 
    soup = BeautifulSoup(html_text, "lxml")

    try: 
        # gets all text content from citations
        content = soup.find('ol', class_ ='references')
        idx = 1

        citations = content.find_all('li')
        citation_obj_array = []
        citation_num = 1

        # creates array of objects
        for single_citation in citations: 
            empty_citation = my_citation("", "", citation_num)
            citation_num+=1
            citation_obj_array.append(empty_citation)

        single_counter = 0
        # grabs the relevant text 
        for single_citation in citations: 
            citation_text = single_citation.get_text()
            # ignore first 2 chars and remove \n
            citation_text = citation_text[2:].rstrip()
            # populate object
            citation_obj_array[single_counter].text= citation_text
            # print(citation_obj_array[single_counter].text)
            single_counter += 1


        link_counter = 0
        # if it exists, grabs the link associated to text 
        reference_wrapper = soup.find_all('span', class_="reference-text")
        for single_citation in reference_wrapper: 
            # if it has a link, add it 
            if single_citation.find_all('a', href=True):
            # if single_citation.find('cite'):
                for a in single_citation.find_all('a', href=True): 
                    # print(a['href'])
                    citation_obj_array[link_counter].link = a['href']
                    link_counter +=1
                    break
            else: 
                link_counter +=1
                continue

        return citation_obj_array
    except: 
        empty_citation = my_citation("", "No available citation data", -3)
        citation_obj_array = [empty_citation]
        return citation_obj_array


@app.get('/photos/{lang}/{tag}')
# gets the links and the citations to the photos
def get_photos(lang: str, tag: str):
    languageURL = "https://en.wikipedia.org/wiki/"
    # Defaults to english if no language specified
    if(lang == "fr"): 
        languageURL = "https://fr.wikipedia.org/wiki/"
    if(lang == "it"): 
        languageURL = "https://it.wikipedia.org/wiki/"
    if(lang == "es"): 
        languageURL = "https://es.wikipedia.org/wiki/"
    if(lang == "ru"): 
        languageURL = "https://ru.wikipedia.org/wiki/"

    url = languageURL + tag
    html = requests.get(url) 
    html_text = "none"
    if(html.status_code==200): 
        html_text = requests.get(url).text
        
    else: 
        print(f"Failed get request from webpage with code {html.status_code}")
        return "Could not reach Wikipedia page.  Either the page does not exist or Wikipedia is currently unreachable."
        # exit(0)
    
    # format the text in lxml format 
    soup = BeautifulSoup(html_text, "lxml")

    try: 
        images_array = []
        # create empty array of image obj
        for _ in soup.find_all('a', class_="image"): 
            empty_img_obj = my_image("", "", 0)
            images_array.append(empty_img_obj)

        # get infobox image first(if it exists)
        if(soup.find_all("td", class_="infobox-image")): 
            # text caption 
            info_caption = soup.find("td", class_="infobox-image").get_text()

            # find the image src
            info_wrapper = soup.find_all("td", class_="infobox-image")
            for a in info_wrapper: 
                for k in a.find_all('img', src=True): 
                    # add the https in front 
                    img_src = k['src']
                    img_src = "https:" + img_src
            
            # populate tthe infobox
            images_array[0].src = img_src
            images_array[0].caption = info_caption
            images_array[0].id = 1

        image_text_idx = 0
        image_src_idx = 0
        # if there is a title image, populate 2nd array in list
        if(images_array[0].id == 1): 
            image_text_idx = 1
            image_src_idx = 1

        # find and populate the image caption 
        other_images = soup.find_all("div", class_="thumb")
        for image in other_images: 
            image_caption = image.get_text()
            images_array[image_text_idx].caption = image_caption
            image_text_idx += 1

        # find and populate the image source 
        image_wrapper = soup.find_all("div", class_="thumbinner")
        for wrapper in image_wrapper: 
            for tag in wrapper.find_all('img', class_="thumbimage", src=True):
                img_src = tag['src']
                img_src = "https:" + img_src
                images_array[image_src_idx].src = img_src
                image_src_idx += 1

        final_images_array = []

        # remove image instances with no source
        for finalImage in images_array: 
            if len(finalImage.src) == 0:
                continue
            final_images_array.append(finalImage)

        # for finalImage in final_images_array: 
        #     print(f"Image source: {finalImage.src}")
        #     print(f"Image caption: {finalImage.caption}")
        #     print(f"Image id: {finalImage.id}")

        return final_images_array
    except: 
        return []

@app.get('/categories/{lang}/{tag}')
# gets the related categories
def get_categories(lang: str, tag: str):

    languageURL = "https://en.wikipedia.org/wiki/"
    
    # Defaults to english if no language specified
    if(lang == "fr"): 
        languageURL = "https://fr.wikipedia.org/wiki/"
    if(lang == "it"): 
        languageURL = "https://it.wikipedia.org/wiki/"
    if(lang == "es"): 
        languageURL = "https://es.wikipedia.org/wiki/"
    if(lang == "ru"): 
        languageURL = "https://ru.wikipedia.org/wiki/"

    url = languageURL + tag
    html = requests.get(url) 
    html_text = "none"
    if(html.status_code==200): 
        html_text = requests.get(url).text
    else: 
        print(f"Failed get request from webpage with code {html.status_code}")
        return "Could not reach Wikipedia page.  Either the page does not exist or Wikipedia is currently unreachable."
        # exit(0)
    
    # format the categories raw html in lxml format 
    soup = BeautifulSoup(html_text, "lxml")
    try: 
        categories_wrapper = soup.find("div", class_="mw-normal-catlinks")
        categories_array = []
        # empty category array 
        for category in categories_wrapper.find_all('li'): 
            empty_category_obj= my_category("", "")
            categories_array.append(empty_category_obj)

        # get title for each category
        text_idx = 0
        for category in categories_wrapper.find_all('li'):
            categories_array[text_idx].text = category.get_text()
            text_idx += 1
        
        # get link for each category 
        link_idx = 0
        for single_category in categories_wrapper.find_all('ul'): 
            for tag in single_category.find_all('a'): 
                category_link = tag['href']
                category_link = languageURL + category_link
                categories_array[link_idx].link = category_link
                link_idx+=1    
        return categories_array
    except: 
        empty_category = my_category("", "No categories data")
        return  [empty_category]

@app.get('/chapters/{lang}/{tag}')
# gets each chapter in the article
def get_chapters(lang: str, tag: str):
    languageURL = "https://en.wikipedia.org/wiki/"

    # Defaults to english if no language specified
    if(lang == "fr"): 
        languageURL = "https://fr.wikipedia.org/wiki/"
    if(lang == "it"): 
        languageURL = "https://it.wikipedia.org/wiki/"
    if(lang == "es"): 
        languageURL = "https://es.wikipedia.org/wiki/"
    if(lang == "ru"): 
        languageURL = "https://ru.wikipedia.org/wiki/"

    url = languageURL + tag
    html = requests.get(url) 
    html_text = "none"
    if(html.status_code==200): 
        html_text = requests.get(url).text
    else: 
        print(f"Failed get request from webpage with code {html.status_code}")
        exit(0)

    # format the text in lxml format 
    soup = BeautifulSoup(html_text, "lxml")

    try: 
        # gets all text content from page
        content = soup.find('div', class_ ='toc')
        myList = content.find('ul')
        myTags = myList.find_all('a')

        chaptersArray = []
        finalArray = []
        # all the chapters are here, extract the content in href
        for chapter in myTags: 
            madeChapter = chapter['href']
            doneChapter = madeChapter[1:]
            chaptersArray.append(doneChapter)

        for chapter in chaptersArray: 
            chapterLink = languageURL + tag + "#" + chapter
            chapterObject = my_chapter(chapterLink, chapter)
            finalArray.append(chapterObject)
        return finalArray
    except: 
        empty_chapter = my_chapter("", "No chapters data")
        return  [empty_chapter]


# url = 'https://en.wikipedia.org/wiki/Lexus_F'
# url = 'https://en.wikipedia.org/wiki/WWE'
# url = 'https://en.wikipedia.org/wiki/Wally_Buhaj'
# url = 'https://en.wikipedia.org/wiki/Lexus_IS_(XE20)'
# translated-news
This is a simple automation project

Steps of automation:

1. GET api from cryptopanic website (get all news and also hot news by filtering api calling url)
2. News from cryptopanic is translated into Malay language using an API from an ai agent created under easypeasy for accurate translation
3. Spesific prompt is then given to the ai agent to make an accurate translation
4. Then the results of translation for both hot news and all news is shown
5. save it into a translated_news.json file
6. functions from (1-5) is in cryptonews_translator.py file
7. The translated_news.json file is then called into index.html for public view
8. in html the hot news and all news are shown separately with a toggle function using inline javascript in the html file
9. Then a workflow is created to run every hour
10. The workflow will run cryptonews_translator.py and push the latest translated_news.json that it got from the python script into this repository
11. This complete the steps for automation, thus adding translated news from cryptopanic api into our own server


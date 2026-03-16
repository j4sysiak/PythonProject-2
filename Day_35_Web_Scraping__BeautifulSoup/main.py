from bs4 import BeautifulSoup
import requests

# 1. Pobieramy cały kod HTML strony
response = requests.get("https://news.ycombinator.com/")
yc_web_page = response.text

# 2. Tworzymy obiekt "zupy" (BeautifulSoup), który przetrawi ten kod
soup = BeautifulSoup(yc_web_page, "html.parser")

# 3. Wyciągamy wszystkie tytuły (w HTML Hacker News są w tagach <span class="titleline">)
articles = soup.find_all(name="span", class_="titleline")

# 4. Wyciągamy pierwszy artykuł (nazwa + link)
first_article = articles[0]
article_text = first_article.getText()
article_link = first_article.find("a").get("href")

print(f"Najpopularniejszy artykuł: {article_text}")
print(f"Link: {article_link}")
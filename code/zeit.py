#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
from datetime import date


# Article Klasse die die zu scrapenden Daten speichert
class Article:
    def __init__(self, headline, link, text_body, source, source_name, author, topic, crawl_date, creation_date):
        self.headline = headline
        self.link = link
        self.text_body = text_body
        self.source = source
        self.source_name = source_name
        self.author = author
        self.topic = topic
        self.crawl_date = crawl_date
        self.creation_date = creation_date

    # Helfer Methode die es später ermöglicht einen JSON String zu erstellen
    # siehe return von 'def get_articles()'
    def serialize(self):
        return {
            'headline': self.headline,
            'textBody': self.text_body,
            'source': self.source,
            'source_name': self.source_name,
            'author': self.author,
            'topic': self.topic,
            'link': self.link,
            'crawl_date': self.crawl_date,
            'creation_date': self.creation_date,
        }


# Sucht sich die eine Liste mit allen Artikel links zusammen
def get_news_links(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    item = soup.find_all('div', class_='cp-region')

    links = []
    for item in item:
        if item.find('a'):
            links.append(item.find('a').get('href').strip())
    return links

# Extrahiert alle notwendigen informationen von einem einzigen Artikel
def scrape(link):
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    [s.extract() for s in soup('script')]  # entfernt alle script tags
    
    # HEADLINE
    headline = ''
    if len(soup.find_all('span', class_='article-heading__title')) > 0:
        headline = soup.find_all('span', itemprop='name')[0].get_text()
    print(headline)

    # TOPIC
    topic = ''
    if len(soup.find_all('span', itemprop='name')) > 0:
        topic = soup.find_all('span', itemprop='name')[0].get_text()

    # AUTHOR
    author = ''
    if len(soup.find_all('div', class_='byline', itemprop='name')) > 0:
        author = soup.find_all('div', class_='byline', itemprop='name')[0].find().get_text()

#   TEXT_BODY
    text_body = ''
    if len(soup.find_all('div', class_='article-body article-body--article'))> 0:
        text_body = soup.find_all('div', class_='article-body article-body--article')[0].find().get_text()
    text_body = ' '.join(text_body.split())  # entfernt alle überschüssigen whitespaces und Zeilenumbrüche

    # CREATION_DATE
    creation_date = ''
    if soup.find('time'):
        creation_date = soup.find('time').get('datetime')

    return Article(headline, link, text_body, 'https://www.zeit.de', 'zeit', author, topic, date.today(), creation_date)


# ************************* Flask web app *************************  #


app = Flask(__name__)


# Hier wird der Pfad(route) angegeben der den scraper arbeiten lässt.
# In dem Fall ist die URL "localhost:5000/zeit"
@app.route('/zeit')
def get_articles():
    links = get_news_links('https://www.zeit.de')
    articles = []
    for link in links:
        articles.append(scrape(link))
    return jsonify([e.serialize() for e in articles])  # jsonify erzeugt aus einem Objekt einen String im JSON Format


@app.route('/')
def index():
    return "<h1>Hier passiert nichts. Bitte gehe zu 'localhost:5000/zeit</h1>"


# Web Application wird gestartet
if __name__ == '__main__':
    app.run()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

import requests
from bs4 import BeautifulSoup, Tag


class Takoboto:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://takoboto.jp',
    }
    COOKIES = {
        'ARRAffinity': 'c903c2edbec777d29417d2fc31a5aa4e11c31ce3c98d9807f3e16b67a76fba63',
        'WAWebSiteSID': '6ffccf72ac53405086348fc7dcdd9837',
    }

    def __init__(self):
        self.session = requests.Session()

    def construct_url(self, level):
        return f'https://takoboto.jp/lists/study/n{level}vocab/?page='

    def write_csv(self, level, list_words):
        with open(f'takoboto_n{level}_vocab.csv', 'a+') as f:
            for word, kana, english, see_more in list_words:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow([word, kana, english, see_more])

    def crawl_vocab_by_level(self, level: int = 5):
        if level < 1 or level > 5:
            raise ValueError('Level must be between 1 and 5')
        last_page = self.get_pages(self.construct_url(level) + '1')
        for i in range(1, last_page + 1):
            list_words = self.crawl_vocab_by_page(self.construct_url(level), i)
            self.write_csv(level, list_words)

    def crawl_vocab_by_page(self, host, page=0):
        print(f'crawling page {page}')
        url = host + str(page)
        req = self.session.get(url, headers=self.HEADERS, cookies=self.COOKIES)
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text, 'html.parser')
        result_div = soup.find_all('div', class_='ResultDiv')
        list_words = []
        for block in result_div:
            if block:
                word_and_kana = block.contents[1].text
                word, kana = self.get_name_and_kana(word_and_kana)
                english = self.get_all_text(block)
                see_more = 'https://takoboto.jp' + block.contents[-1].find('a').get('href')
                list_words.append((word, kana, english, see_more))
        return list_words

    def get_name_and_kana(self, word_and_kana):
        wk = word_and_kana.split(',', 1)
        if len(wk) == 2:
            word = wk[0].strip()
            kana = wk[1].strip()
            print(f'word: {word}, kana: {kana}')
            return word, kana
        return wk, ''

    def get_all_text(self, block):
        texts = ""
        for content in block.contents:
            if isinstance(content, Tag):
                if content.get_text() != '':
                    texts += (content.get_text()) + "\n"
            else:
                if content != '':
                    texts += content + "\n"
        texts = texts.replace('See more >  common', '')
        return texts

    def get_pages(self, url):
        req = self.session.get(url, headers=self.HEADERS, cookies=self.COOKIES)
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text, 'html.parser')
        # find all tag with class 'PageLink' and return last one text
        return int(soup.find_all('a', class_='PageLink')[-1].text)


if __name__ == '__main__':
    takoboto = Takoboto()
    takoboto.crawl_vocab_by_level(5)

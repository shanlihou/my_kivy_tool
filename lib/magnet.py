# coding= utf-8
import requests
from bs4 import BeautifulSoup
import urllib
import re
import sys
import gzip
import os
from common import config
URIBASE = None
DYNAMIC_URI = 'https://tellme.pw/btsow'


def get_headers():
    return {
        'Host': URIBASE, 
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3053.3 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 
        'Connection': 'keep-alive', 
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'
    }


def save_file(data):
    with open('one.html', 'w', encoding='utf-8') as fw:
        fw.write(data)


def get_save(fn=None):
    if not fn:
        fn = 'test.html'
    with open(fn, 'r', encoding='utf-8') as fr:
        return fr.read()


def get_content(urlPath, is_save=False):
    ret = requests.get(urlPath, headers=get_headers())
    html = ret.text
    if is_save:
        save_file(html)
    return html


class BtOne(object):
    def __init__(self, url, size, name):
        self.mag = url
        self.size = size
        self.name = name

    def __str__(self):
        return '{},{}'.format(self.mag, self.size)

    def parse_mag(self, content):
        pat = re.compile(r'(magnet:\?xt=urn:btih:[^"><]+)["<>]')
        ret = pat.findall(content)
        return ret[0]


def rec_content(content):
    rets = []
    for inner in content.contents:
        if hasattr(inner, 'contents'):
            rets.append(rec_content(inner))
        else:
            rets.append(inner)

    return ''.join(rets)


def parse_content(content):
    soup = BeautifulSoup(content, "html.parser")
    div = soup.select('div[class="data-list"]')
    for _div in div:
        for ret in _div.select('div[class="row"]'):
            a = ret.select('a')[0]
            name = a.select('div')[0]
            name = rec_content(name)
            size = a.find_next_siblings('div')[0].string
            url = a['href']
            hash_code = url.split('/')[-1]
            mag = 'magnet:?xt=urn:btih:{}'.format(hash_code)
            yield BtOne(mag, size, name)


def parse_cur_url(data):
    soup = BeautifulSoup(data, "html.parser")
    strongs = soup.select('strong')
    for strong in strongs:
        a = strong.select('a')[0]
        return rec_content(a)

def get_cur_uri(isSave=False):
    ret = requests.get(DYNAMIC_URI)
    if isSave:
        with open(os.path.join('tmp', 'pellow'), 'w') as fw:
            fw.write(ret.text)

    return parse_cur_url(ret.text)

def _get_all_magnet(code):
    code = urllib.parse.quote(code)
    url = 'https://{}/search/{}'.format(URIBASE, code)
    content = get_content(url, False)
    ret_list = []
    for bo in parse_content(content):
        ret_list.append((bo.mag, bo.name, bo.size))
    
    return ret_list

def get_all_magnet(code):
    # code=urllib.quote_plus(code)
    global URIBASE
    cur_url = config.Config().get('cur_url')
    if not config.Config().get('cur_url'):
        cur_url = get_cur_uri()
        config.Config().set_val('cur_url', cur_url)
    
    URIBASE = cur_url[len('https://'):]
    try:
        ret = _get_all_magnet(code)
        return ret
    except:
        cur_url = get_cur_uri()
        config.Config().set_val('cur_url', cur_url)
        URIBASE = cur_url[len('https://'):]
        return _get_all_magnet(code)


def main():
    ret = get_all_magnet('复仇者')
    print(ret)


if __name__ == '__main__':
    parse_content(get_save())
    #     bo = BtOne(1)
    # getAllMagnet('复仇者')
#     if (len(sys.argv) == 2):
#         getAllMagnet(sys.argv[1])

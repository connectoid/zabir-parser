
from pprint import pprint
import base64
import os
from random import shuffle
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

base_url = 'https://zabir.ru'
test_url = 'https://zabir.ru/past/simpl/pravila/5/klass/'

load_dotenv()
app_password = os.getenv('app_password')
user = "poster"
credentials = user + ':' + app_password
token = base64.b64encode(credentials.encode())
header = {'Authorization': 'Basic ' + token.decode('utf-8')}


def create_post(post_json):
    url = "https://eskant-foto.ru/wp-json/wp/v2/posts"
    content = create_content(post_json['images'])
    post = {
        'title': post_json['title'],
        'content': content,
        'status': 'publish',
        # 'fifu_image_url': 'https://avatars.mds.yandex.net/i?id=4bf81673746c3d4eb5f00e50985a1a8b_l-10713392-images-thumbs&n=13',
        # 'fifu_image_alt': 'fifu_image_alt'
        # 'featured_media': 0,
    }
    response = requests.post(url , headers=header, json=post)
    # print(response.json())


def create_content(image_json):
    content = []
    for image in image_json:
        html_image_block = f"""
        <p>
            <a href={image['src']} target="_blank">
                <picture style="padding-top:75%">
                    <img 
                        width="711"
                        loading="lazy" 
                        decoding="async" 
                        alt="{image['alt']}" 
                        title="{image['title']}"
                        src="{image['src']}" 
                        data-src="{image['data-src']}"
                    >
                </picture>
            </a>
        <span>{image['title']}</span>
        </p>
        """
        content.append(html_image_block)
    content = (' ').join(content)
    return content


def get_posts(url):
    posts_list = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        post_divs = soup.find_all('div', class_='post')
        post_divs = [div for div in post_divs if div.find('h2')]
        for post in post_divs:
            post_dict = {}
            post_dict['title'] = post.find('h2').find('a').text
            post_dict['url'] = base_url + post.find('h2').find('a')['href']
            posts_list.append(post_dict)
        return posts_list
    else:
        print(f'Request Error: {response.status_code}')
        return False
    

def get_images_from_post(url):
    images_list = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        pictures = soup.find_all('picture')
        images = [picture.find('img') for picture in pictures]
        for img in images:
            image_dict = {}
            image_dict['alt'] = img['alt']
            image_dict['title'] = img['title']
            image_dict['src'] = img['src']
            try:
                image_dict['data-src'] = img['data-src']
            except:
                image_dict['data-src'] = ''
            images_list.append(image_dict)
        return images_list
    else:
        print(f'Request Error: {response.status_code}')
        return False


def main():
    time1 = datetime.now()
    count = 0
    max_posts = 50
    posts = []
    post_json = {}
    posts = get_posts(base_url)
    shuffle(posts)
    for post in posts:
        post_json['title'] = post['title']
        images_list = get_images_from_post(post['url'])
        shuffle(images_list)
        images = []
        for image in images_list:
            image_json = {}
            image_json['title'] = image['title']
            image_json['alt'] = image['alt']
            image_json['src'] = image['src']
            image_json['data-src'] = image['data-src']
            images.append(image_json)
        post_json['images'] = images
        count += 1
        print(f'{count}. Добавлен пост {post_json["title"]}')
        # if count >= max_posts:
        #     break

        result = create_post(post_json)
        time2 = datetime.now()
        print(f'Время парсинга одной страницы: {time2 - time1}')


if __name__ == '__main__':
    main()
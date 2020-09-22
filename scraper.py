import requests
from bs4 import BeautifulSoup
from utils import save_json, make_dir, mock_response, load_json, divide_chunks, shorten_url, make_soup
from multiprocessing import Pool
import os
import re
# from selenium import webdriver
from time import sleep
import json

base_url = 'https://kfebrakes.com/catalog/'

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/83.0.4103.116 Safari/537.36 '


class ProductList:

    def fetch_meta_list(self):
        if os.path.exists('meta_list.json'):
            return

        meta_list = []
        year_list = self.fetch_year_list()
        for year_item in year_list:
            make_model_list = self.fetch_make_model_list(year_item)
            print(year_item, make_model_list)
            for make_item in make_model_list:
                for model_item in make_item['model_list']:
                    meta_list.append({
                        'year_item': year_item,
                        'make_item': make_item['name'],
                        'model_item': model_item
                    })
        save_json(meta_list, 'meta_list.json')

    def scrape(self):
        meta_list = load_json('meta_list.json')
        # self.export(meta_list[0])
        pool = Pool(50)
        pool.map(self.export, meta_list)

    def export(self, meta_item):

        output_file_path = 'output/data/' + meta_item['make_item']
        make_dir(output_file_path)
        output_file_path += '/' + meta_item['model_item'].replace('/', '#')
        make_dir(output_file_path)

        output_file_name = output_file_path + '/' + meta_item['year_item'] + '.json'
        if os.path.exists(output_file_name):
            return

        product_list = self.fetch_product_list(
            meta_item['make_item'],
            meta_item['model_item'],
            meta_item['year_item']
        )

        if product_list is None:
            print('*** Error:', output_file_name, '***')
            return

        save_json(product_list, output_file_name)
        print(output_file_name)


    def fetch_year_list(self):
        response = requests.get(base_url)
        soup = make_soup(response.text)

        result = []
        container = soup.find('select', attrs={'id': 'year_select'})
        for item in container.findAll('option'):
            if item['value'] != 'default':
                result.append(item.text)
        return result

    def fetch_make_model_list(self, year_item):
        url = 'https://kfebrakes.com/wp-content/plugins/kfe-catalog/kfe-catalog-get-cars.php' \
              '?year=' + year_item
        response = requests.get(url)

        if response.text == '':
            return []
        response = json.loads(response.text)

        result = []

        make_list = list(response.keys())
        for make_item in make_list:
            model_list = []
            model_indexes = list(response[make_item].keys())
            for index in model_indexes:
                model_list.append(response[make_item][index])
                result.append({
                    'name': make_item,
                    'model_list': model_list
                })

        return result

    def fetch_product_list(self, make_item, model_item, year_item):
        url = 'https://kfebrakes.com/wp-content/plugins/kfe-catalog/kfe-catalog-get-data.php' \
              '?make=' + make_item + \
              '&model=' + model_item.replace(' ', '+') + \
              '&year=' + year_item

        result = []

        response = requests.get(url)
        soup = make_soup(response.text)

        for item in soup.findAll('tr'):
            cells = item.findAll('td')

            if len(cells) != 6:
                return None

            front_pad = cells[3]
            rear_pad = cells[4]

            result.append({
                'model': cells[0].text.strip(),
                'year': cells[1].text.strip(),
                'trim': cells[2].text.strip(),
                'front_pad': front_pad.text.strip(),
                'front_pad_url': front_pad.find('a')['href'] if front_pad.find('a') is not None else '',
                'rear_pad': rear_pad.text.strip(),
                'rear_pad_url': rear_pad.find('a')['href'] if rear_pad.find('a') is not None else '',
                'note': cells[5].text.strip()
            })

        return result


class ProductDetails:

    def scrape(self):
        product_list = []
        with os.scandir('output/data') as it1:
            for make_entry in it1:
                if os.path.isdir(make_entry):
                    with os.scandir(make_entry.path) as it2:
                        for model_entry in it2:
                            if os.path.isdir(model_entry):
                                with os.scandir(model_entry.path) as it3:
                                    for year_entry in it3:
                                        if year_entry.name.endswith('.json'):
                                            data = load_json(year_entry.path)
                                            for item in data:
                                                if item['front_pad_url'] != '':
                                                    product_list.append(item['front_pad_url'])

                                                if item['rear_pad_url'] != '':
                                                    product_list.append(item['rear_pad_url'])

        product_list = list(dict.fromkeys(product_list))

        temp = product_list
        product_list = []
        for item in temp:
            file_name = 'output/products/' + shorten_url(item) + '.json'
            if os.path.exists(file_name):
                continue
            product_list.append(item)

        print('===', len(product_list), '===')

        # self.export(product_list[0])
        pool = Pool(50)
        pool.map(self.export, product_list)

    def export(self, url):
        file_name = 'output/products/' + shorten_url(url) + '.json'
        if os.path.exists(file_name):
            return

        response = requests.get(url)
        soup = make_soup(response.text)

        if self.get_product_name(soup) is None:
            print('*** Error:', url, '***')
            return

        if self.get_specifications(soup) is None:
            print('*** Error Table:', url, '***')
            return

        if self.get_applications(soup) is None:
            print('*** Error Application:', url, '***')
            return

        details = {
            'product_name': self.get_product_name(soup),
            'specifications': self.get_specifications(soup),
            'applications': self.get_applications(soup),
            'image_url': self.get_image_url(soup)
        }

        save_json(details, file_name)
        print(file_name)

    def get_product_name(self, soup):
        container = soup.find('div', attrs={'id': 'pageHeader'})
        if container is None or container.find('h1') is None:
            return None
        return container.find('h1').text.strip()

    def get_specifications(self, soup):
        container = soup.find('table')
        result = []

        if container is None:
            return None

        for row in container.findAll('tr'):
            cells = row.findAll('td')
            if len(cells) == 2:
                result.append(cells[0].text.strip() + '|' + cells[1].text.strip())
        return result

    def get_applications(self, soup):
        all_cols = soup.findAll('div', attrs={'column'})

        result = []
        for index, item in enumerate(all_cols):
            if index > 1 and item.find('h4') is not None:
                if item.find('p') is None:
                    continue

                result.append(item.find('h4').text.strip())

                model_list = item.find('p').text.strip().split('\n')
                for model_item in model_list:
                    result.append(model_item.strip())

        return result

    def get_image_url(self, soup):
        container = soup.find('div', attrs={'class': 'column oneHalf'})
        return container.find('img')['src']






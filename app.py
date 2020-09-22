import os
from utils import load_json, save_json, make_dir, download_image, flatten_list
from scraper import ProductList, ProductDetails, make_soup
from excel_exporter import export_excel, get_product_details
from multiprocessing import  Pool
import requests
# from selenium import webdriver

make_dir('output')
make_dir('output/excel')
make_dir('output/data')
make_dir('output/products')
make_dir('output/images')


def export_compatibility_list():
    with os.scandir('output/compatibility_list/raw') as it:
        for entry in it:
            if entry.name.endswith('.json'):
                data = load_json(entry.path)

                output_data = []

                with open('output/compatibility_list/' + entry.name.replace('.json', '.txt') , 'w') as f:
                    f.write(flatten_list(output_data))


def download_images():
    image_meta_list = []
    image_url_list = []

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
                                                front_details = get_product_details(item['front_pad_url'])
                                                if front_details is not None:
                                                    if front_details['image_url'] not in image_url_list:
                                                        image_url_list.append(front_details['image_url'])
                                                        image_meta_list.append({
                                                            'url': front_details['image_url'],
                                                            'path': 'output/images/',
                                                            'file_name': item['front_pad']
                                                        })

                                            if item['rear_pad_url'] != '':
                                                rear_details = get_product_details(item['rear_pad_url'])
                                                if rear_details is not None:
                                                    if rear_details['image_url'] not in image_url_list:
                                                        image_url_list.append(rear_details['image_url'])
                                                        image_meta_list.append({
                                                            'url': rear_details['image_url'],
                                                            'path': 'output/images/',
                                                            'file_name': item['rear_pad']
                                                        })

    print('===', len(image_meta_list), '===')
    pool = Pool(50)
    pool.map(download_image, image_meta_list)


if __name__ == '__main__':
    product_list = ProductList()
    # product_list.fetch_meta_list()
    # product_list.scrape()

    product_details = ProductDetails()
    # product_details.scrape()

    # product_details.export('https://kfebrakes.com/products/quiet-advanced-ceramic-brake-pads/kfe1107a-104')
    #
    export_excel()
    #
    # download_images()

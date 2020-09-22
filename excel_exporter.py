import xlsxwriter
import os
from utils import load_json, flatten_list, shorten_url
from functools import reduce


def get_product_details(url):
    file_name = 'output/products/' + shorten_url(url) + '.json'

    if os.path.exists(file_name):
        return load_json(file_name)
    else:
        print('\nFile not found', file_name)
        return None


def export(make_entry):
    workbook = xlsxwriter.Workbook('output/excel/' + make_entry.name + '.xlsx', {'strings_to_urls': False})
    worksheet = workbook.add_worksheet('')

    worksheet.write('A1', 'ProductURL')
    worksheet.write('B1', 'Make')
    worksheet.write('C1', 'Model')
    worksheet.write('D1', 'Year')
    worksheet.write('E1', 'Trim')
    worksheet.write('F1', 'YearRange')
    worksheet.write('G1', 'Position')
    worksheet.write('H1', 'Note')
    worksheet.write('I1', 'ProductNumber')
    worksheet.write('J1', 'ProductName')
    worksheet.write('K1', 'Specifications')
    worksheet.write('L1', 'Applications')
    worksheet.write('M1', 'ImageURL')

    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:F', 15)
    worksheet.set_column('G:H', 25)
    worksheet.set_column('I:M', 30)

    row, col = 1, 0

    with os.scandir(make_entry.path) as it1:
        for model_entry in it1:
            if os.path.isdir(model_entry):
                with os.scandir(model_entry.path) as it2:
                    for year_entry in it2:
                        if year_entry.name.endswith('.json'):
                            data_file = load_json(year_entry.path)

                            for item in data_file:
                                front = item['front_pad_url']
                                if front != '':
                                    front_details = get_product_details(item['front_pad_url'])

                                    worksheet.write(row, col, item['front_pad_url'])
                                    worksheet.write(row, col + 1, make_entry.name)
                                    worksheet.write(row, col + 2, model_entry.name.replace('#', ''))
                                    worksheet.write(row, col + 3, year_entry.name.replace('.json', ''))
                                    worksheet.write(row, col + 4, item['trim'])
                                    worksheet.write(row, col + 5, item['year'])
                                    worksheet.write(row, col + 6, 'FRONT PAD')
                                    worksheet.write(row, col + 7, item['note'])

                                    worksheet.write(row, col + 8, item['front_pad'])

                                    if front_details is not None:
                                        worksheet.write(row, col + 9, front_details['product_name'])
                                        worksheet.write(row, col + 10, flatten_list(front_details['specifications']))
                                        worksheet.write(row, col + 11, flatten_list(front_details['applications']))
                                        worksheet.write(row, col + 12, front_details['image_url'])

                                    print('\r', make_entry.name, row, end='')
                                    row += 1

                                rear = item['rear_pad_url']
                                if rear != '':
                                    rear_details = get_product_details(item['rear_pad_url'])

                                    worksheet.write(row, col, item['rear_pad_url'])
                                    worksheet.write(row, col + 1, make_entry.name)
                                    worksheet.write(row, col + 2, model_entry.name.replace('#', ''))
                                    worksheet.write(row, col + 3, year_entry.name.replace('.json', ''))
                                    worksheet.write(row, col + 4, item['trim'])
                                    worksheet.write(row, col + 5, item['year'])
                                    worksheet.write(row, col + 6, 'REAR PAD')
                                    worksheet.write(row, col + 7, item['note'])

                                    worksheet.write(row, col + 8, item['rear_pad'])

                                    if rear_details is not None:
                                        worksheet.write(row, col + 9, rear_details['product_name'])
                                        worksheet.write(row, col + 10, flatten_list(rear_details['specifications']))
                                        worksheet.write(row, col + 11, flatten_list(rear_details['applications']))
                                        worksheet.write(row, col + 12, rear_details['image_url'])

                                    print('\r', make_entry.name, row, end='')
                                    row += 1

    workbook.close()


def export_excel():
    with os.scandir('output/data') as it:
        for entry in it:
            if os.path.isdir(entry.path):
                export(entry)

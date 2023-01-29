#!/usr/bin/env python

import requests


api_key = 'e843669b-8640-423c-a5c0-ec71dc5e047d' # TODO: move to config file (in gitignore)


'''
collegiate dictionary api reference: https://dictionaryapi.com/products/api-collegiate-dictionary
json data format api reference: https://dictionaryapi.com/products/json
'''

word = 'bat'

url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'
print(url)

response = requests.get(url)
if response.status_code == 200:
    print([s[0][1]['dt'][0][1] for s in response.json()[0]['def'][0]['sseq']])



# TODO
# from PyDictionary import PyDictionary


# dictionary = PyDictionary()

# bat = dictionary.meaning('bat')
# # print(bat.keys())
# # print(bat.values())
# for key, value in bat.items():
#     print(f'{key}: {value}')

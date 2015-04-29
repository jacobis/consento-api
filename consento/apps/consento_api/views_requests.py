# encoding: utf-8

'''
Updated on Apr 28, 2015

@author: Jacob Sungwoon Lee
'''

import requests
import logging


logger = logging.getLogger('api')


def venue_search_request(url, params):
    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = response.json()
    response = response.get('response')

    venue_list = []

    for doc in response.get('docs'):
        object_id = doc.get('pObjectID')
        name = doc.get('pNames')[0]
        address = doc.get('pAddresses')[0]
        location = doc.get('pLatLong')
        category = doc.get('pCategory')[0]
        total_count = doc.get('pTotalComments')
        positive_comments = doc.get('pPositiveComments')
        negative_comments = doc.get('pNegativeComments')
        pos_rate = None

        if positive_comments and negative_comments:
            pos_rate = float(positive_comments) / float(positive_comments + negative_comments) * 100
        
        venue = {
            'object_id': object_id,
            'name': name,
            'address': address,
            'location': location,
            'category': category,
            'total_count': total_count,
            'positive_comments': positive_comments,
            'negative_comments': negative_comments,
            'pos_rate': pos_rate
        }
        venue_list.append(venue)
        
    return venue_list


def venue_home_request(url, params):
    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = response.json()
    top_keywords = response.get('TopKeywords')
    response = response.get('response')

    venue_list = []
    keyword_list = []

    for index, obj in enumerate(response.get('docs')):
        object_id = obj.get('pObjectID')
        name = obj.get('pNames')[0]
        address = obj.get('pAddresses')[0]
        location = obj.get('pLatLong')
        category = obj.get('pCategory')[0]
        image = obj.get('image')
        rank = index + 1

        try:
            related_keyword = [tp['name'] for tp in obj.get('pTopPhrase')]
        except:
            related_keyword = None

        venue = {
            'object_id': object_id,
            'name': name,
            'address': address,
            'location': location,
            'category': category,
            'image': image,
            'rank': rank,
            'related_keyword': related_keyword
        }

        venue_list.append(venue)

    for index, top_keyword in enumerate(top_keywords.get('RESTAURANT')):
        keyword = {
            'name': top_keyword[0],
            'rank': index + 1
        }

        keyword_list.append(keyword)

    result = {'venue': venue_list, 'keyword': keyword_list}

    return result


def venue_keyword_request(url, params):
    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = bs(response.content)

    ontology = response.find('doc', {'name': 'Ontology'})
    if params['q'] == 'good':
        city_networks = ast.literal_eval(find_by_name(ontology, 'str', 'cityNetwork'))[:10]
    else:
        city_networks = ast.literal_eval(find_by_name(ontology, 'str', 'cityNetwork'))[:5]

    keyword_list = []

    for index, cn in enumerate(city_networks):
        keyword = cn.get('name')
        keyword_list.append({'rank': index+1, 'keyword': keyword})

    return keyword_list
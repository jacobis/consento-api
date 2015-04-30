# encoding: utf-8

'''
Updated on Apr 28, 2015

@author: Jacob Sungwoon Lee
'''

import ast
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


def venue_detail_request(url, params):
    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = response.json()
    response = response.get('response')
    response = response.get('docs')[0]

    # Meta
    name = response.get('pNames')[0]
    category = response.get('pCategory')[0]
    address = response.get('pAddresses')[0]
    location = response.get('pLatLong')
    phone_number = response.get('pPhoneNumbers')[0]
    yelp_id = response.get('id')
    yelp_bizs = response.get('pKey_yelp')
    yelp_biz = None
    yelp_url = None

    if yelp_bizs:
        yelp_biz = yelp_bizs[0]
        yelp_url = 'http://www.yelp.com/biz/' + yelp_biz


    meta = {'name': name, 'category': category, 'address': address, 'location': location, 'phone_number': phone_number, 'yelp_id': yelp_id, 'yelp_url': yelp_url}

    # Doc Count
    doc_count = response.get('pTotalComments')
    total_doc = doc_count

    # Image
    image = response.get('image')

    # Keyword
    keyword = None
    keyword_new = None

    # Overall
    positive = response.get('pPositiveComments')
    negative = response.get('pNegativeComments')
    overall = {'positive': positive, 'negative': negative}

    # Pref Relateds
    pref_related = response.get('pPrefRelated')
    meal_type_list = pref_related.get('MealType')
    profile_list = pref_related.get('Profile')
    purpose_list = pref_related.get('Purpose')

    # Meal Type
    meal_types = {}
    for meal_type in meal_type_list:
        name = meal_type.get('name')
        freq = meal_type.get('freq')
        meal_types[name] = freq

    # profiles
    profiles = {}
    for profile in profile_list:
        name = profile.get('name')
        freq = profile.get('freq')
        profiles[name] = freq

    gluten_free = None
    gluten_free_avg = None
    gluten_free_related = None
    vegan = profiles.get('Vegan')
    vegan_avg = aspect_avg(vegan, total_doc)
    vegan_related = None
    vegetarian = profiles.get('Vegetarian')
    vegetarian_avg = aspect_avg(vegetarian, total_doc)
    vegetarian_related = None
    profiles = {
        'gluten_free': gluten_free, 
        'gluten_free_avg': gluten_free_avg,
        'gluten_free_related': gluten_free_related,
        'vegan': vegan, 
        'vegan_avg': vegan_avg,
        'vegan_related': vegan_related,
        'vegetarian': vegetarian,
        'vegetarian_avg': vegetarian_avg,
        'vegetarian_related': vegetarian_related
    }

    # purposes
    purposes = {}
    for purpose in purpose_list:
        name = purpose.get('name')
        freq = purpose.get('freq')
        purposes[name] = freq

    family = purposes.get('Family')
    family_avg = aspect_avg(family, total_doc)
    family_related = None
    noise = purposes.get('Noise')
    noise_avg = aspect_avg(noise, total_doc)
    noise_related = None
    view = purposes.get('View')
    view_avg = aspect_avg(view, total_doc)
    view_related = None
    wait = purposes.get('Waiting')
    wait_avg = aspect_avg(wait, total_doc)
    wait_related = None
    purposes = {
        'family': family, 
        'family_avg': family_avg,
        'family_related': family_related,
        'noise': noise, 
        'noise_avg': noise_avg,
        'noise_related': noise_related,
        'view': view, 
        'view_avg': view_avg,
        'view_related': view_related,
        'wait': wait,
        'wait_avg': wait_avg,
        'wait_related': wait_related
    }

    venue = {'meta': meta, 'doc_count': doc_count, 'overall': overall, 'image': image, 'keyword': keyword, 'keyword_new': keyword_new, 'meal_type': meal_types, 'dietary': profiles, 'venue_preference': purposes}

    return venue


def aspect_avg(aspect, total_doc, total_aspect=155150, total_segment=40063501):
    aspect_avg = (float(aspect) / float(total_doc)) / (float(total_aspect) / float(total_segment)) if aspect and total_doc else None
    return aspect_avg
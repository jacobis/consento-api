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
        category = doc.get('type')
        total_count = doc.get('pTotalComments')
        doc_count = doc.get('numFoundSeg')
        positive_comments = doc.get('pPositiveComments')
        negative_comments = doc.get('pNegativeComments')
        pos_rate = None
        storecd = None #Dummy for error

        if positive_comments and negative_comments:
            pos_rate = float(positive_comments) / float(positive_comments + negative_comments) * 100
        
        venue = {
            'object_id': object_id,
            'name': name,
            'address': address,
            'location': location,
            'category': category,
            'total_count': total_count,
            'doc_count': doc_count,
            'positive_comments': positive_comments,
            'negative_comments': negative_comments,
            'pos_rate': pos_rate,
            'storecd': storecd #Dummy for error
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
        category = obj.get('type')
        rank = index + 1
        yelp_bizs = obj.get('pKey_yelp')
        image = get_image(yelp_bizs) if yelp_bizs else None

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
            'keyword': top_keyword[0],
            'rank': index + 1,
            'related': get_keyword_related(top_keyword[0])
        }

        keyword_list.append(keyword)

    result = {'venue': venue_list, 'keyword': keyword_list}

    return result


def venue_keyword_request(url, params):
    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = response.json()
    top_keywords = response.get('TopKeywords')

    keyword_list = []

    for index, top_keyword in enumerate(top_keywords.get('RESTAURANT')):
        keyword = {
            'keyword': top_keyword[0],
            'rank': index + 1
        }

        keyword_list.append(keyword)

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
    category = response.get('category')[0]
    address = response.get('pAddresses')[0]
    location = response.get('pLatLong')
    phone_number = response.get('pPhoneNumbers')[0]
    yelp_id = response.get('id')
    yelp_bizs = response.get('pKey_yelp')
    yelp_biz = None
    yelp_url = None
    image = None

    if yelp_bizs:
        yelp_biz = yelp_bizs[0]
        yelp_url = 'http://www.yelp.com/biz/' + yelp_biz
        image = get_image(yelp_bizs)

    meta = {'name': name, 'category': category, 'address': address, 'location': location, 'phone_number': phone_number, 'yelp_id': yelp_id, 'yelp_url': yelp_url}

    # Doc Count
    doc_count = response.get('pTotalSegNum')
    total_doc = doc_count

    # Keyword
    try:
        keyword = [{'name':tp['name'], 'rank':tp['rank'], 'count':tp['Human'], 'related':None} for tp in response.get('pTopPhrase')]
    except:
        keyword = None

    # Overall
    positive = response.get('pPositiveComments')
    negative = response.get('pNegativeComments')
    overall = {'positive': positive, 'negative': negative}

    # Pref Relateds
    pref_related = response.get('pPrefRelated')
    gluten_free_list = pref_related.get('Gluten_Free')
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

    for gluten_free in gluten_free_list:
        name = gluten_free.get('name')
        freq = gluten_free.get('freq')
        profiles[name] = freq

    # purposes
    purposes = {}
    for purpose in purpose_list:
        name = purpose.get('name')
        freq = purpose.get('freq')
        purposes[name] = freq

    gluten_free = profiles.get('Gluten Free')
    gluten_free_avg = aspect_avg(gluten_free, total_doc)
    gluten_free_related = None
    vegan = profiles.get('Vegan')
    vegan_avg = aspect_avg(vegan, total_doc)
    vegan_related = None
    vegetarian = profiles.get('Vegetarian')
    vegetarian_avg = aspect_avg(vegetarian, total_doc)
    vegetarian_related = None
    dietary = {
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

    dating = purposes.get('Dating')
    dating_avg = aspect_avg(dating, total_doc)
    dating_related = None
    family = purposes.get('Family')
    family_avg = aspect_avg(family, total_doc)
    family_related = None
    friend = purposes.get('Friend')
    friend_avg = aspect_avg(friend, total_doc)
    friend_related = None
    noise = profiles.get('Noise')
    noise_avg = aspect_avg(noise, total_doc)
    noise_related = None
    parking = profiles.get('Parking')
    parking_avg = aspect_avg(parking, total_doc)
    parking_related = None
    view = profiles.get('View')
    view_avg = aspect_avg(view, total_doc)
    view_related = None
    wait = profiles.get('Waiting')
    wait_avg = aspect_avg(wait, total_doc)
    wait_related = None
    venue_preference = {
        'dating': dating,
        'dating_avg': dating_avg,
        'dating_related': dating_related,
        'family': family, 
        'family_avg': family_avg,
        'family_related': family_related,
        'friend': friend, 
        'friend_avg': friend_avg,
        'friend_related': friend_related,
        'noise': noise, 
        'noise_avg': noise_avg,
        'noise_related': noise_related,
        'parking': parking,
        'parking_avg': parking_avg,
        'parking_related': parking_related,
        'view': view, 
        'view_avg': view_avg,
        'view_related': view_related,
        'wait': wait,
        'wait_avg': wait_avg,
        'wait_related': wait_related
    }

    venue = {'meta': meta, 'doc_count': {'total_doc': doc_count}, 'overall': overall, 'image': image, 'keyword': keyword, 'meal_type': meal_types, 'dietary': dietary, 'venue_preference': venue_preference}

    return venue


def aspect_avg(aspect, total_doc, total_aspect=155150, total_segment=40063501):
    aspect_avg = (float(aspect) / float(total_doc)) / (float(total_aspect) / float(total_segment)) if aspect and total_doc else None
    return aspect_avg


def get_image(key):
    url = 'http://popoplocal.com/image/getList/' + ','.join(key)
    response = requests.get(url, timeout=5)
    response.raise_for_status()

    response = response.json()

    thumbnails = response[0].get('thumbnails')
    thumbnail = thumbnails[0] if thumbnails else None

    return thumbnail


def get_keyword_related(keyword):
    url = 'http://solrcloud0-320055289.us-west-1.elb.amazonaws.com/s'
    params = {'ocat': 1, 't': 'lt'}

    location = 'San Francisco, CA'
    query = keyword

    params['locreg'] = location
    params['q'] = query

    try:
        response = requests.get(url, params=params, timeout=5)
        logger.info('GET url : %s' % response.url)
        response.raise_for_status()

    except requests.exceptions.Timeout as e:
        context = "Error occurred during Connection with consento server"
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')
    try:
        response = response.json()
        top_keywords = response.get('TopKeywords').get('RESTAURANT')

        top_keywords = '\t'.join(top_keyword[0] for top_keyword in top_keywords)
    except:
        top_keywords = None
    
    return top_keywords
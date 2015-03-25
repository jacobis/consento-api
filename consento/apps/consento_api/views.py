# encoding: utf-8

'''
Created on Aug 26, 2014

@author: Ju Kyung Lee, Jacob Sungwoon Lee
'''

import ast
import re
import json
import logging
import requests
from bs4 import BeautifulSoup as bs

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from libs.utils.beautifulsoup_wrapper import find_by_name
from libs.utils.coordinate import coordinate_swapper
from libs.utils.json_wrapper import wrap_success_json, wrap_failure_json

from .models import Venue


logger = logging.getLogger('api')

@csrf_exempt
def venue_search(request):
    if request.method == 'GET':
        '''
        Return venue list ordered by consento rank-base.

        Args:
            vid: vender id (*)
            location: city, state (* Need location or latlng)
            latlng: latitude, longitude (* Need location or latlng)
            query: any query

            (e.g.) 
            with Location :
                curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search?location=San+Jose,CA&query=pizza"

            with Coordinate :
                curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search?latlng=37.756,-122.454,37.856,-122.354&location=San+Jose,CA&query=pizza"

        Return:
            Result data is following format:
            {"data": 
                {"and_result": [{"category": "Restaurants", "name": "Maggiano\u2019s Little Italy", "object_id": "8273929", "doc_count": "50", "storecd": "2876", "address": "3055 Olin Ave San Jose, CA 95128", "location": "37.3208463,-121.9496176"}], 
                "or_result": [{"category": "Restaurants", "name": "Maggiano\u2019s Little Italy", "object_id": "8273929", "doc_count": "483", "storecd": "2876", "address": "3055 Olin Ave San Jose, CA 95128", "location": "37.3208463,-121.9496176"}]
                }
            }
        '''

        try:
            url = 'http://ec2-54-183-94-75.us-west-1.compute.amazonaws.com/s'
            params = {'ocat': 1, 'fl': '*', 't': 'lt'}

            try:
                latlng = request.GET['latlng'].split(',')
            except:
                latlng = None

            try:
                location = request.GET['location']
            except:
                location = None

            if latlng:
                latlng = coordinate_swapper(latlng)
                params['latlng'] = ",".join(str(ll) for ll in latlng)

            if location:
                params['location'] = location

            try:
                original_queries = request.GET['query']
                params['q'] = original_queries
                or_result = venue_search_request(url, params)
                
                queries = ''
                for query in original_queries.split(' '):
                    queries += '+(%s) ' % query
                params['q'] = queries
                and_result = venue_search_request(url, params)

                venue_list = {'and_result': and_result, 'or_result': or_result}

            except:
                venue_list = venue_search_request(url, params)

            context = wrap_success_json(venue_list)
            logger.info('Response JSON : %s' % context)

            return HttpResponse(context, status=200, content_type='application/json')
        
        except requests.exceptions.Timeout as e:
            context = "Error occurred during Connection with 9platters"
            return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

        except Exception as e:
            context = "Exception Error"
            logger.info('Error : %s' % e)
            return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

    else:
        context = 'Allowed only GET method'
        return HttpResponse(wrap_failure_json(context), status=405, content_type='application/json')

@csrf_exempt
def venue_home(request):
    try:
        url = 'http://ec2-54-183-94-75.us-west-1.compute.amazonaws.com/s'
        params = {'ocat': 1, 'fl': '*', 't': 'lt'}

        try:
            latlng = request.GET['latlng'].split(',')
        except:
            latlng = None

        try:
            location = request.GET['location']
        except:
            location = None

        if latlng:
            latlng = coordinate_swapper(latlng)
            params['latlng'] = ",".join(str(ll) for ll in latlng)

        if location:
            params['location'] = location

        params['q'] = 'pizza'

        result = venue_home_request(url, params)
        context = wrap_success_json(result)
        logger.info('Response JSON : %s' % context)

        return HttpResponse(context, status=200, content_type='application/json')

    except requests.exceptions.Timeout as e:
        context = "Error occurred during Connection with 9platters"
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

    except Exception as e:
        context = "Exception Error"
        logger.info('Error : %s' % e)
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')


@csrf_exempt
def venue_keyword(request):
    try:
        url = 'http://9platters.com/s'
        params = {'t': 'l', 'dr': '24', 'wt': 'xml'}

        try:
            latlng = request.GET['latlng'].split(',')
        except:
            latlng = None
        try:
            location = request.GET['location'].split(',')
        except:
            location = None
        try:
            keyword = request.GET['keyword']
        except:
            keyword = 'good'

        if latlng:
            latlng = coordinate_swapper(latlng)
            params['latmin'] = latlng[0]
            params['lngmin'] = latlng[1]
            params['latmax'] = latlng[2]
            params['lngmax'] = latlng[3]

        if location:
            params['ocity'] = location[0]
            params['ostate'] = location[1]

        if keyword:
            params['q'] = keyword

        keyword_list = venue_keyword_request(url, params)
        context = wrap_success_json(keyword_list)
        logger.info('Response JSON : %s' % context)

        return HttpResponse(context, status=200, content_type='application/json')

    except requests.exceptions.Timeout as e:
        context = "Error occurred during Connection with 9platters"
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

    except Exception as e:
        context = "Exception Error"
        logger.info('Error : %s' % e)
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')


def venue_search_request(url, params):
    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = response.json()
    response = response.get('response')

    venue_list = []

    doc_count = response.get('numfound')

    for obj in response.get('docs'):
        if doc_count == 1: continue
        name = obj.get('pNames')[0]
        address = obj.get('pAddresses')[0]
        location = obj.get('pLatLong')
        category = obj.get('pCategory')[0]
        object_id = obj.get('pObjectID')
        total_count = obj.get('pTotalComments')
        positive_comments = obj.get('pPositiveComments')
        negative_comments = obj.get('pNegativeComments')
        pos_rate = positive_comments / (positive_comments + negative_comments) * 100
        venue = {
            'name': name,
            'address': address,
            'location': location,
            'category': category,
            'object_id': object_id,
            'total_count': total_count,
            'doc_count': str(doc_count),
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

        address = obj.get('pAddresses')[0]
        category = obj.get('pCategory')[0]
        image = obj.get('image')
        location = obj.get('pLatLong')
        name = obj.get('pNames')[0]
        object_id = obj.get('pObjectID')
        rank = index + 1

        try:
            related_keyword = [tp['name'] for tp in obj.get('pTopPhrase')]
        except:
            related_keyword = []

        venue = {
            'address': address,
            'category': category,
            'image': image,
            'location': location,
            'name': name,
            'object_id': object_id,
            'rank': rank,
            'related_keyword': related_keyword
        }

        venue_list.append(venue)

    result = {'venue': venue_list, 'keyword': top_keywords}

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


def venue_detail(request, venue_id):
    try:
        object_id = "pObjectID:" + venue_id

        url = 'http://ec2-54-183-94-75.us-west-1.compute.amazonaws.com/s'
        params = {'q': object_id, 'fl': '*'}

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
        phone_number = response.get('pPhoneNumbers')[0]
        yelp_id = response.get('id')
        yelp_biz = response.get('pKey_yelp')[0]
        yelp_url = 'http://www.yelp.com/biz/' + yelp_biz if yelp_biz else None
        location = response.get('pLatLong')
        meta = {'name': name, 'category': category, 'address': address, 'phone_number': phone_number, 'yelp_id': yelp_id, 'yelp_url': yelp_url, 'location': location}

        # Doc Count
        doc_count = response.get('pTotalComments')
        total_doc = doc_count

        # Image
        image = response.get('image')

        # Keyword
        keyword = {}
        keyword_new = {}

        # Overall
        positive = response.get('pPositiveComments')
        negative = response.get('pNegativeComments')
        overall = {'positive': positive, 'negative': negative}

        # Pref Relateds
        pref_related = response.get('pPrefRelated')
        pref_relateds = {}
        for pr in pref_related:
            for pr in pr.values():
                for i in pr:
                    pref_relateds.update(i)
        
        # Meal Type
        breakfast = pref_relateds.get('Breakfast')
        brunch = pref_relateds.get('Brunch')
        lunch = pref_relateds.get('Lunch')
        dinner = pref_relateds.get('Dinner')
        dessert = pref_relateds.get('Dessert')
        meal_type = {'breakfast': breakfast, 'brunch': brunch, 'lunch': lunch, 'dinner': dinner, 'dessert': dessert}

        # Dietary & Venue Preference
        gluten_free = ""
        gluten_free_avg = ""
        gluten_free_related = ""
        vegan = pref_relateds.get('Vegan')
        vegan_avg = aspect_avg(vegan, total_doc)
        vegan_related = ""
        vegetarian = pref_relateds.get('Vegetarian')
        vegetarian_avg = aspect_avg(vegetarian, total_doc)
        vegetarian_related = ""
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

        family = pref_relateds.get('Family')
        family_avg = aspect_avg(family, total_doc)
        family_related = ""
        noise = pref_relateds.get('Noise')
        noise_avg = aspect_avg(noise, total_doc)
        noise_related = ""
        view = pref_relateds.get('View')
        view_avg = aspect_avg(view, total_doc)
        view_related = ""
        wait = pref_relateds.get('Waiting')
        wait_avg = aspect_avg(wait, total_doc)
        wait_related = ""
        venue_preference = {
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

        venue = {'meta': meta, 'doc_count': doc_count, 'overall': overall, 'image': image, 'keyword': keyword, 'keyword_new': keyword_new, 'meal_type': meal_type, 'dietary': dietary, 'venue_preference': venue_preference}

        context = wrap_success_json(venue)

        return HttpResponse(context, status=200, content_type='application/json')

    except requests.exceptions.Timeout as e:
        context = "Error occurred during Connection with 9platters"
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

    except Exception as e:
        context = "Exception Error"
        logger.info('Error : %s' % e)
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')


def aspect_avg(aspect, total_doc, total_aspect=155150, total_segment=40063501):
    return (float(aspect) / float(total_doc)) / (float(total_aspect) / float(total_segment))


def image_finder(key):
    image_objects = Venue.objects.filter(key=key, version="2014")
    
    if not image_objects:
        image_objects = Venue.objects.filter(key=key, version="2014_additional")

    images = [image_object.image_url for image_object in image_objects]

    return images

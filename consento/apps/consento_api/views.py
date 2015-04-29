# encoding: utf-8

'''
Updated on Apr 28, 2015

@author: Jacob Sungwoon Lee
'''

import ast
import re
import requests
import json
import logging

from bs4 import BeautifulSoup as bs

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from libs.utils.coordinate import coordinate_swapper
from libs.utils.json_wrapper import wrap_success_json, wrap_failure_json

from .views_requests import *


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
            with Query:
                with Location :
                    curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search?location=San%20Jose,%20CA&query=pizza"
                with Coordinate :
                    curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search?latlng=37.756,-122.454,37.856,-122.354&query=pizza"

            without Query:
                with Location :
                    curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search?location=San%20Jose,%20CA"
                with Coordinate :
                    curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search?latlng=37.756,-122.454,37.856,-122.354"

        Return:
            Result data is following format:
            {"data": 
                {"and_result": [{"category": "Cheese Shops", "pos_rate": 94.39449014731204, "positive_comments": 4934, "name": "The Cheese Board", "address": "1504 Shattuck Ave Berkeley, CA 94709, United States", "total_count": "7657", "negative_comments": 293, "object_id": "31483", "location": "37.8799415,-122.2693075"}], 
                "or_result": [{"category": "Pizza", "pos_rate": 88.58851052768391, "positive_comments": 3408, "name": "800 Degrees Neapolitan Pizzeria", "address": "10889 Lindbrook Dr Los Angeles, CA 90024, United States", "total_count": "5693", "negative_comments": 439, "object_id": "163214", "location": "34.059930827289,-118.44431695965"}]
                }
            }
        '''

        try:
            url = 'http://solrcloud0-320055289.us-west-1.elb.amazonaws.com/s'
            params = {'ocat': 1, 't': 'o'}

            try:
                latlng = request.GET['latlng'].split(',')
            except:
                latlng = None

            try:
                location = request.GET['location']
            except:
                location = None

            try:
                query = request.GET['query']
            except:
                query = None

            if latlng:
                latlng = coordinate_swapper(latlng)
                params['latlng'] = ",".join(str(ll) for ll in latlng)

            if location:
                params['locreg'] = location

            if query:
                params['q'] = query
                params['t'] = 'lt'
                
            try:
                # or_result
                or_result = venue_search_request(url, params)

                # and_result
                queries = ''
                for q in query.split(' '):
                    queries += '+(%s) ' % q
                params['q'] = queries
                and_result = venue_search_request(url, params)

                venue_list = {'and_result': and_result, 'or_result': or_result}

            except:
                venue_list = venue_search_request(url, params)

            context = wrap_success_json(venue_list)
            logger.info('Response JSON : %s' % context)

            return HttpResponse(context, status=200, content_type='application/json')
        
        except requests.exceptions.Timeout as e:
            context = "Error occurred during Connection with consento server"
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
    if request.method == 'GET':
        '''
        Return recommended venue list ordered by consento rank-base.

        Args:
            vid: vender id (*)
            location: city, state (* Need location or latlng)
            latlng: latitude, longitude (* Need location or latlng)

            (e.g.) 
            with Location :
                curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/home?location=San%20Jose,%20CA"
            with Coordinate :
                curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/home?latlng=37.756,-122.454,37.856,-122.354"

        Return:
            Result data is following format:
            {"data": 
                {"venue": [{"category": "Sushi Bars", "rank": 1, "name": "Cha Cha Sushi", "address": "547 W Capitol Expy San Jose, CA 95136, United States", "image": "http://54.67.62.180/2014/restaurants/ca/san_jose/cha-cha-sushi-san-jose/1.jpg", "related_keyword": ["Brandon roll", "Cha Cha Sushi", "Cha Cha Sushi"], "object_id": "219448", "location": "37.275925,-121.85314"}], 
                "keyword": [{"name": "orange sauce", "rank": 1}, {"name": "green tea ice cream", "rank": 2}, {"name": "Santana Row", "rank": 3}, {"name": "La Vic", "rank": 4}, {"name": "sushi place", "rank": 5}, {"name": "Cha Cha Sushi", "rank": 6}, {"name": "carne asada", "rank": 7}, {"name": "Pizza Antica", "rank": 8}, {"name": "dim sum", "rank": 9}, {"name": "ramen place", "rank": 10}]
                }
            }
        '''

        try:
            url = 'http://solrcloud0-320055289.us-west-1.elb.amazonaws.com/s'
            params = {'ocat': 1, 't': 'o'}

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
                params['locreg'] = location

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

    else:
        context = 'Allowed only GET method'
        return HttpResponse(wrap_failure_json(context), status=405, content_type='application/json')


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

@csrf_exempt
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
        yelp_biz = response.get('pKey_yelp')[0] if response.get('pKey_yelp') else None
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

        if pref_related:
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
        gluten_free = None
        gluten_free_avg = None
        gluten_free_related = None
        vegan = pref_relateds.get('Vegan')
        vegan_avg = aspect_avg(vegan, total_doc)
        vegan_related = None
        vegetarian = pref_relateds.get('Vegetarian')
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

        family = pref_relateds.get('Family')
        family_avg = aspect_avg(family, total_doc)
        family_related = None
        noise = pref_relateds.get('Noise')
        noise_avg = aspect_avg(noise, total_doc)
        noise_related = None
        view = pref_relateds.get('View')
        view_avg = aspect_avg(view, total_doc)
        view_related = None
        wait = pref_relateds.get('Waiting')
        wait_avg = aspect_avg(wait, total_doc)
        wait_related = None
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
    aspect_avg = (float(aspect) / float(total_doc)) / (float(total_aspect) / float(total_segment)) if aspect and total_doc else None
    return aspect_avg
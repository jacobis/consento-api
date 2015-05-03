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
            logger.info('Response JSON - Venue Search : %s' % context)

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
            logger.info('Response JSON - Home : %s' % context)

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
            query = request.GET['keyword']
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

        keyword_list = venue_keyword_request(url, params)
        context = wrap_success_json(keyword_list)
        logger.info('Response JSON - Keyword : %s' % context)

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
    '''
    Return specific venue information.

    Args:
        vid: vender id (*)
        venue_id: venue id (*)

        (e.g.) 
        curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/62915"
        
    Return:
        Result data is following format:
        {"data": 
            {"meta": {"category": "Nightlife", "phone_number": "415 474 5044", "yelp_id": "62915!metaDoc", "location": "37.806698,-122.42074", "address": "2765 Hyde Street at Beach Street San Francisco, CA, United States", "yelp_url": "http://www.yelp.com/biz/buena-vista-cafe-san-francisco", "name": "Buena Vista"}
            }
        }
    '''

    try:
        object_id = "pObjectID:" + venue_id

        url = 'http://solrcloud0-320055289.us-west-1.elb.amazonaws.com/s'
        params = {'q': object_id}

        venue = venue_detail_request(url, params)

        context = wrap_success_json(venue)
        logger.info('Response JSON - Detail : %s' % context)

        return HttpResponse(context, status=200, content_type='application/json')

    except requests.exceptions.Timeout as e:
        context = "Error occurred during Connection with 9platters"
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

    except Exception as e:
        context = "Exception Error"
        logger.info('Error : %s' % e)
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

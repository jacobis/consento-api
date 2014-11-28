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
                curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search?latlng=37.76625,-122.42212&query=pizza"

        Return:
            Result data is following format:
            {"data": 
                {"and_result": [{"category": "Restaurants", "name": "Maggiano\u2019s Little Italy", "object_id": "8273929", "doc_count": "50", "storecd": "2876", "address": "3055 Olin Ave San Jose, CA 95128", "location": "37.3208463,-121.9496176"}], 
                "or_result": [{"category": "Restaurants", "name": "Maggiano\u2019s Little Italy", "object_id": "8273929", "doc_count": "483", "storecd": "2876", "address": "3055 Olin Ave San Jose, CA 95128", "location": "37.3208463,-121.9496176"}]
                }
            }
        '''

        try:
            url = 'http://9platters.com/tgrape'
            params = {'t': 'l', 'dr': '24', 'wt': 'xml'}

            try:
                latlng = request.GET['latlng'].split(',')
            except:
                latlng = None

            try:
                location = request.GET['location'].split(',')
            except:
                location = None

            if latlng:
                latlng = coordinate_swapper(latlng)

                if len(latlng) == 4:
                    params['latmin'] = latlng[0]
                    params['lngmin'] = latlng[1]
                    params['latmax'] = latlng[2]
                    params['lngmax'] = latlng[3]
                else:
                    params['lat'] = latlng[0]
                    params['lng'] = latlng[1]
                    params['sr'] = float(4.02336)

            if location:
                params['ocity'] = location[0]
                params['ostate'] = location[1]

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

                # queries_list = request.GET['query'].split(' ')
                # if len(queries_list) >= 2:
                #     params['q'] = ' '.join(queries_list)
                #     or_result = venue_search_request(url, params)

                #     queries = ''.join('+(' + query + ')' for query in queries_list)
                #     params['q'] = queries
                #     and_result = venue_search_request(url, params)

                #     venue_list = {'and_result': and_result, 'or_result': or_result}
                # else:
                #     params['q'] = ' '.join(queries_list)
                #     venue_list = venue_search_request(url, params)

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

        if latlng:
            params['lat'] = latlng[0]
            params['lng'] = latlng[1]
            params['sr'] = float(4.02336)

        if location:
            params['ocity'] = location[0]
            params['ostate'] = location[1]

        params['q'] = 'good'

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
        print e
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
            keyword = None

        if latlng:
            params['lat'] = latlng[0]
            params['lng'] = latlng[1]
            params['sr'] = float(4.02336)

        if location:
            params['ocity'] = location[0]
            params['ostate'] = location[1]

        if keyword:
            params['keyword'] = keyword

        venue_list = venue_keyword_request(url, params)
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


def venue_search_request(url, params):

    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = bs(response.content)
    objects = response.find_all('object')

    venue_list = []

    for obj in objects:
        doc_count = int(obj.get('numfound'))
        if doc_count == 1: continue
        name = find_by_name(obj, 'str', 'pName')
        address = find_by_name(obj, 'str', 'oaddr')
        location = find_by_name(obj, 'str', 'latlong')
        category = find_by_name(obj, 'str', 'pYelpCategory')
        try:
            storecd = find_by_name(obj, 'str', 'STORECD')
        except:
            storecd = ''
        object_id = obj.get('id')
        total_count = find_by_name(obj, 'int', 'pTotalComments')
        positive_comments = find_by_name(obj, 'int', 'pPositiveComments')
        negative_comments = find_by_name(obj, 'int', 'pNegativeComments')
        pos_rate = find_by_name(obj, 'float', 'pPosNeg')
        venue = {
            'name': name,
            'address': address,
            'location': location,
            'category': category,
            'storecd': storecd,
            'object_id': object_id,
            'total_count': total_count,
            'doc_count': doc_count,
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

    response = bs(response.content)
    objects = response.find_all('object')

    venue_list = []
    keyword_list = []

    for obj in objects:
        name = find_by_name(obj, 'str', 'pName')
        address = find_by_name(obj, 'str', 'oaddr')
        location = find_by_name(obj, 'str', 'latlong')
        category = find_by_name(obj, 'str', 'pYelpCategory')
        venue = {
            'name': name,
            'address': address,
            'location': location,
            'category': category
        }

        venue_list.append(venue)

    ontology = response.find('doc', {'name': 'Ontology'})
    city_networks = ast.literal_eval(find_by_name(ontology, 'str', 'cityNetwork'))

    for index, cn in enumerate(city_networks):
        keyword = cn.get('name')
        related = cn.get('relatedKeyword')
        keyword_list.append({'rank': index+1, 'keyword': keyword, 'related': related})

    result = {'venue': venue_list, 'keyword': keyword_list}

    return result


def venue_keyword_request(request, params):
    response = requests.get(url, params=params, timeout=5)
    logger.info('GET url : %s' % response.url)
    response.raise_for_status()

    response = bs(response.content)

    pass


def venue_detail(request, venue_id):
    
    try:
        object_id = 'oid:' + venue_id

        url = 'http://9platters.com/s'
        params = {'q': object_id, 't': 'd', 'wt': 'xml'}

        response = requests.get(url, params=params, timeout=5)
        logger.info('GET url : %s' % response.url)
        response.raise_for_status()

        response = bs(response.content)

        # Meta
        meta = response.find('doc', {'name': 'ObjectMeta'})
        name = find_by_name(meta, 'str', 'pName')
        category = find_by_name(meta, 'str', 'pYelpCategory')
        address = find_by_name(meta, 'str', 'pAddress')
        phone_number = find_by_name(meta, 'str', 'pPhoneNumber')
        yelp_id = find_by_name(meta, 'str', 'id')
        yelp_url = find_by_name(meta, 'str', 'pYelpBiz')
        yelp_url = 'http://www.yelp.com/biz/' + yelp_url if yelp_url else None
        location = find_by_name(meta, 'str', 'pLatLong')
        meta = {'name': name, 'category': category, 'address': address, 'phone_number': phone_number, 'yelp_id': yelp_id, 'yelp_url': yelp_url, 'location': location}

        # Doc Count
        total_doc = response.find('result', {'name': 'response'}).get('numsegs')
        doc_count = {'total_doc': total_doc}
        
        # Overall
        ontology = response.find('doc', {'name': 'Ontology'})
        positive = find_by_name(ontology, 'int', 'pos')
        negative = find_by_name(ontology, 'int', 'neg')
        overall = {'positive': positive, 'negative': negative}

        # Keyword
        top_phrase_offline = find_by_name(ontology, 'str', 'topPhraseOffline')
        keyword_list = re.split('\t|/', top_phrase_offline)[::2]
        keyword = {}
        i = 0
        for k in keyword_list:
            keyword[k] = len(keyword_list) - i
            i = i + 1

        # Meal Type
        other_times = find_by_name(ontology, 'str', 'othersTimes')
        other_times = other_times.replace(',];', ']')
        exec(other_times)
        other_times = {}
        for datum in data:
            name = datum.get('name').strip(' ')
            value = datum.get('value')
            other_times[name] = value

        breakfast = other_times.get('Breakfast')
        brunch = other_times.get('Brunch')
        lunch = other_times.get('Lunch')
        dinner = other_times.get('Dinner')
        dessert = other_times.get('Dessert')
        meal_type = {'breakfast': breakfast, 'brunch': brunch, 'lunch': lunch, 'dinner': dinner, 'dessert': dessert}

        # Dietary & Venue Preference
        combo_buttons = find_by_name(ontology, 'str', 'ComboButtons')
        combo_buttons = combo_buttons.replace(',];', ']')
        exec(combo_buttons)
        combo_buttons = {}
        for datum in data:
            name = datum.get('name').strip(' ')
            frequency = datum.get('frequency')
            pos = datum.get('pos')
            neg = datum.get('neg')
            combo_buttons[name] = {'frequency': frequency, 'pos': pos, 'neg': neg}

        gluten_free = combo_buttons.get('Gluten Free').get('frequency')
        vegan = combo_buttons.get('Vegan').get('frequency')
        vegetarian = combo_buttons.get('Vegetarian').get('frequency')
        dietary = {'gluten_free': gluten_free, 'vegan': vegan, 'vegetarian': vegetarian}

        family = combo_buttons.get('Family').get('frequency')
        noise = combo_buttons.get('Noise').get('frequency')
        view = combo_buttons.get('View').get('frequency')
        wait = combo_buttons.get('Waiting').get('frequency')
        venue_preference = {'family': family, 'noise': noise, 'view': view, 'wait': wait}

        venue = {'meta': meta, 'doc_count': doc_count, 'overall': overall, 'keyword': keyword, 'meal_type': meal_type, 'dietary': dietary, 'venue_preference': venue_preference}

        context = wrap_success_json(venue)

        return HttpResponse(context, status=200, content_type='application/json')

    except requests.exceptions.Timeout as e:
        context = "Error occurred during Connection with 9platters"
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')

    except Exception as e:
        context = "Exception Error"
        logger.info('Error : %s' % e)
        return HttpResponse(wrap_failure_json(context), status=500, content_type='application/json')
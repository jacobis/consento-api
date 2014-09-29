# encoding: utf-8

'''
Created on Aug 26, 2014

@author: Ju Kyung Lee, Jacob Sungwoon Lee
'''

import re
import json
import logging
import requests
from bs4 import BeautifulSoup as bs

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from libs.utils.json_wrapper import wrap_success_json, wrap_failure_json
from libs.utils.beautifulsoup_wrapper import find_by_name

logger = logging.getLogger('api')

@csrf_exempt
def venue_search(request):
    if request.method == 'GET':
        '''
        Return venue list ordered by consento rank-base.

        Args:
            vid: vender id (*)
            location: city, state (*)
            query: any query (*)

            (e.g.) curl -i -H "Accept: application/json" -X GET "http://localhost:8000/v1/venues/search/?location=San+Jose,CA&query=birthday+party"

        Return:
            Result data is following format:
            {"data": {"restaurants": ["936129", "1305429", "994629", "917229", "1002629", "1045029", "1091329", "1093029", "1099629", "1091829"]}, "success": true}
        '''

        try:
            query = request.GET['query']
            location = request.GET['location'].split(',')

            url = 'http://9platters.com/tgrape'
            params = {'q': query, 'ostate': location[1], 'ocity': location[0], 't': 'l', 'wt': 'xml'}

            response = requests.get(url, params=params, timeout=5)
            logger.info('GET url : %s' % response.url)
            response.raise_for_status()

            response = bs(response.content)
            objects = response.find_all('object')

            venue_list = []

            for obj in objects:
                name = find_by_name(obj, 'str', 'pName')
                address = find_by_name(obj, 'str', 'oaddr')
                location = find_by_name(obj, 'str', 'latlong')
                category = find_by_name(obj, 'str', 'pYelpCategory')
                try:
                    storecd = find_by_name(obj, 'str', 'STORECD')
                except:
                    storecd = ''
                object_id = obj.get('id')
                doc_count = obj.get('numreviews')
                venue = {
                    'name': name,
                    'address': address,
                    'location': location,
                    'category': category,
                    'storecd': storecd,
                    'object_id': object_id, 
                    'doc_count': doc_count
                }
                venue_list.append(venue)

            context = wrap_success_json({'venues': venue_list})
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


def venue_detail(request, venue_id):
    
    try:
        object_id = 'oid:' + venue_id

        url = 'http://9platters.com/s'
        params = {'q': object_id, 't': 'd', 'wt': 'xml'}

        response = requests.get(url, params=params, timeout=5)
        logger.info('GET url : %s' % response.url)
        response.raise_for_status()

        response = bs(response.content)
        meta = response.find('doc', {'name': 'ObjectMeta'})

        name = find_by_name(meta, 'str', 'pName')
        category = find_by_name(meta, 'str', 'pYelpCategory')
        address = find_by_name(meta, 'str', 'pAddress')
        phone_number = find_by_name(meta, 'str', 'pPhoneNumber')
        yelp_id = find_by_name(meta, 'str', 'id')
        location = find_by_name(meta, 'str', 'pLatLong')
        
        total_doc = find_by_name(meta, 'int', 'pReviews')

        meta = {'name': name, 'category': category, 'address': address, 'phone_number': phone_number, 'yelp_id': yelp_id, 'location': location}
        doc_count = {'total_doc': total_doc}
        
        ontology = response.find('doc', {'name': 'Ontology'})
        positive = find_by_name(ontology, 'int', 'pos')
        negative = find_by_name(ontology, 'int', 'neg')
        overall = {'positive': positive, 'negative': negative}

        top_phrase_offline = find_by_name(ontology, 'str', 'topPhraseOffline')
        keyword_list = re.split('\t|/', top_phrase_offline)[::2]
        keyword = {}
        i = 0
        for k in keyword_list:
            keyword[k] = len(keyword_list) - i
            i = i + 1

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

        vegetarian = combo_buttons.get('Vegetarian').get('frequency')
        dietary = {'vegetarian': vegetarian}

        wait = combo_buttons.get('Waiting').get('frequency')
        family = combo_buttons.get('Kid').get('frequency')
        view = combo_buttons.get('View').get('frequency')
        venue_preference = {'wait': wait, 'family': family, 'view': view}

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
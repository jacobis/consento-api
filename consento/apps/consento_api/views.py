# encoding: utf-8

'''
Created on Aug 26, 2014

@author: Ju Kyung Lee, Jacob Sungwoon Lee
'''

import json
import logging
import requests
from bs4 import BeautifulSoup as bs

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from libs.utils.json_wrapper import wrap_success_json, wrap_failure_json

logger = logging.getLogger('api')

@csrf_exempt
def restaurant_list(request):
    if request.method == 'GET':
        '''
        Return restaurant list ordered by consento rank-base.

        Args:
            vid: vender id (*)
            locate: city, state (*)
            query: any query (*)

            (e.g.) curl -i -H "Accept: application/json" -X GET "http://localhost:8000/restaurants/?locate=San+Jose,CA&query=birthday+party"

        Return:
            Result data is following format:
            {"data": {"restaurants": ["936129", "1305429", "994629", "917229", "1002629", "1045029", "1091329", "1093029", "1099629", "1091829"]}, "success": true}
        '''

        try:
            query = request.GET['query']
            locate = request.GET['locate'].split(',')

            # Create URL.
            url = 'http://9platters.com/tgrape'
            params = {'q': query, 'ostate': locate[1], 'ocity': locate[0], 't': 'l', 'wt': 'xml'}

            response = requests.get(url, params=params, timeout=5)
            logger.info('GET url : %s' % response.url)

            response = bs(response.content)
            objects = response.find_all('object')
            
            objects = [obj.get('id') for obj in objects]

            context = wrap_success_json({'restaurants': objects})
            logger.info('Response JSON : %s' % context)

            return HttpResponse(context, content_type='application/json')
        
        except (requests.HTTPError, requests.HTTPConnectionPool) as e:
            context = "Error occurred during Connection with 9platters"
            return HttpResponse(wrap_failure_json(context), content_type='application/json')

        except:
            context = "Error"
            return HttpResponse(wrap_failure_json(context), content_type='application/json')

    else:
        context = 'Allowed only GET method'
        return HttpResponse(wrap_failure_json(context), content_type='application/json')


def restaurant_detail(request, restaurant_id):
    
    object_id = 'pObjectID:' + restaurant_id

    url = 'http://9platters.com/collection1/select'
    params = {'q': object_id, 'wt': 'xml'}

    response = requests.get(url, params=params, timeout=5)

    print response.content

    return HttpResponse(wrap_success_json('success'), content_type='application/json')
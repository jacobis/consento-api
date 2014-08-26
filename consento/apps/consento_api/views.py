import json
import logging
import requests
from bs4 import BeautifulSoup as bs

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from libs.utils.json_wrapper import wrap_success_json, wrap_failure_json

logger = logging.getLogger('api')

@csrf_exempt
def restaurants(request):
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
            {"restaurants": ["936129", "1305429", "994629", "917229", "1002629", "1045029", "1091329", "1093029", "1099629", "1091829"]}
        '''

        try:
            # Get Parameter from URL.
            query = request.GET['query']

            # Get City, State from locate.
            locate = request.GET['locate'].split(',')
            city = locate[0]
            state = locate[1]

            t = 'l'
            wt = 'xml'

            # Create URL.
            url = 'http://9platters.com/tgrape'
            params = {'q': query, 't': t, 'wt': wt, 'ostate': state, 'ocity': city}

            # Get XML from 9platters.
            response = requests.get(url, params=params, timeout=5)
            logger.info('GET url : %s' % response.url)

            # Parse XML.
            response = bs(response.content)
            objects = response.find_all('object')
            
            objects = [obj.get('id') for obj in objects]

            # Make Context.
            context = {'restaurants': objects}
            context = wrap_success_json(context)
            logger.info('Response JSON : %s' % context)

            return HttpResponse(wrap_success_json(context), content_type='application/json')
        
        except (rqeuests.HTTPError, requests.HTTPConnectionPool) as e:
            context = "Error occurred during Connection with 9platters"
            return HttpResponse(wrap_failure_json(context), content_type='application/json')

        except:
            context = "Error"
            return HttpResponse(wrap_failure_json(context), content_type='application/json')

    else:
        context = 'Allowed only GET method'
        return HttpResponse(wrap_failure_json(context), content_type='application/json')
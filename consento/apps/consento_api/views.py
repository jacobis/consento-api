import requests
import json
from bs4 import BeautifulSoup as bs

from django.http import HttpResponse


def get_restaurants(request):

    # Get Parameter from URL.
    vid = request.GET['vid']
    query = request.GET['query']

    # Get Cite, State from locate.
    locate = request.GET['locate'].split(',')
    cite = locate[0]
    state = locate[1]

    t = 'l'
    wt = 'xml'

    # Create URL.
    url = 'http://9platters.com/s'
    params = {'q': query, 't': t, 'wt': wt, 'ostate': state, 'ocity': cite}

    # Get XML from 9platters.
    response = requests.get(url, params=params)
    response = response.content

    # Parse XML.
    response = bs(response)
    objects = response.find_all('object')
    objects = [obj.get('id') for obj in objects]

    # Make Context.
    json_dic = {'objects': objects}
    context = json.dumps(json_dic)

    return HttpResponse(context, content_type='application/json')
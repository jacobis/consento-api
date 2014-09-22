'''
Created on Aug 22, 2014

@author: Jacob Sungwoon Lee
'''

import json


def wrap_success_json(result):
    """
    JSON warpper for success response.

    Args:
        result: any data

    Return:
        String JSON dump of result data wrapped in the following format:
            {"success": True, "data": <result>}
    """
    json_message = {'data': result}
    return json.dumps(json_message)

def wrap_failure_json(reason, result=None):
    """
    JSON warpper for failure response.

    Args:
        reason: any data
        result: any data

    Return:
        String JSON dump of result data wrapped in the following format:
            {"success": False, "reason": <reason>}
    """
    json_message = {'reason': reason}
    if result:
        json_message.update({'result': result})
    return json.dumps(json_message)
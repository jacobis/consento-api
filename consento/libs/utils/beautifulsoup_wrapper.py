# encoding: utf-8

'''
Created on Sep 22, 2014

@author: Jacob Sungwoon Lee
'''

def find_by_name(bs_object, tag, name):
    try:
        result = bs_object.find(tag, {'name': name}).text
    except:
        result = None

    return result
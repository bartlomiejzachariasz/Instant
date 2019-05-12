import json
import re
import time
import random
from datetime import datetime
import numpy as np

def get_score(value):
    distribution = np.logspace(-1,1,num=10,base=2.5)
    idx = (np.abs(distribution - value)).argmin()
    return idx+1

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def timestamp_to_date(timestmap):
    return datetime.utcfromtimestamp(timestmap).strftime("%Y-%m-%d %H:%M:%S")

def get_photos_info(profile, bins = 10):    
    current_time = time.time()
    photos_in_averaging = 10
    with open('../scrap_data/{}/{}.json'.format(profile,profile)) as f:
        d = json.load(f)
    images = d['GraphImages']
    pattern = "[0-9_]*_n.jpg"
    images_info = dict(photos=[])
    for image in images:
        if len(re.findall(pattern,image['urls'][0]))==0:
            continue
        images_info['photos'].append(dict(file = re.search(pattern,image['urls'][0]).group(),
                                         likes = image['edge_media_preview_like']['count'],
                                          tags = [tag.lower() for tag in image['tags']] if 'tags' in image.keys() else [],
                                         timestamp = image['taken_at_timestamp'],
                                         date = timestamp_to_date(image['taken_at_timestamp'])))

    
    images_info = sorted(images_info['photos'],key=lambda k: k['timestamp'])
    
    expected_score = [None]*photos_in_averaging \
                     +list(running_mean([im['likes'] for im in images_info[:-1]],photos_in_averaging))
    
    for idx,image in enumerate(images_info):
        image.update({"expected":"{}".format(expected_score[idx])})


    result = list(filter(lambda im:im['expected']!='None' and current_time-im['timestamp']>3600*24,images_info))

    
    
    for image in result:
        ratio = image['likes']/float(image['expected'])
        image.update({"ratio":"{}".format(ratio)})
        image.update({"score":get_score(ratio)})
        
    expected_scores_sorted = sorted([im['ratio'] for im in result])
    
    for image in result:
        image.update({"relative_score":int((expected_scores_sorted.index(image['ratio']))/(len(result)/bins))+1})
    return result
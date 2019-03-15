

import requests
import common
import json


def get_all_campaign_data(campaign_id):
    res = requests.get(common.get_campaign_data_url(campaign_id))
    out = json.loads(res.text)
    return out



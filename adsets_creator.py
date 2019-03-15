

import requests
import json
import common
import time
import os


'''
在指定的campaign_id下创建adset
'''
def create_adset(data, group, platform, basic_data):
    json_data = {
        "name": common.get_name(group, platform),
        "status": "ACTIVE",
        "daily_budget": 1000,
        "bid_amount": int(os.environ['bid_amount']),
        "campaign_id": data['campaign_id'],
        "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
        "billing_event": "IMPRESSIONS",
        "attribution_spec": [
            {
                "event_type": "CLICK_THROUGH",
                "window_days": 7
            }
        ],
        "optimization_goal": "OFFSITE_CONVERSIONS",
        "promoted_object": {
            "application_id": "634204786734953",
            "object_store_url": basic_data['object_store_url'][platform.lower()],
            "custom_event_type": "PURCHASE"
        },
        "targeting": data['targeting'],
        "access_token": os.environ['access_token']
    }
    res = requests.post(common.get_adset_url(), json=json_data)
    out = json.loads(res.text)
    res.close()
    if 'id' in out:
        return out['id']
    else:
        return None


'''
ARCHIVED指定的adset，如果account存在过多ARCHIVED的广告，则状态改为PAUSED
'''
def del_adset(adset_id, del_index):
    jdata = {
        "status": "ARCHIVED",
    }
    res = requests.post(common.get_del_adset_url(adset_id), json=jdata)
    out = json.loads(res.text)
    if 'success' in out:
        return True
    elif 'error' in out and 'error_user_title' in out['error'] and 'Ad Account has too many archived adgroups' in out['error']['error_user_title']:
        jdata['status'] = 'PAUSED'
        res = requests.post(common.get_del_adset_url(adset_id), json=jdata)
        out = json.loads(res.text)
        if 'success' in out:
            return True
    if del_index > 10:
        return False
    time.sleep(5)
    return del_adset(adset_id, del_index+1)


'''
根据adset_id拉取adset数据
'''
def get_adset_data(adset_id):
    res = requests.get(common.get_adaset_data_url(adset_id))
    out = json.loads(res.text)
    return out




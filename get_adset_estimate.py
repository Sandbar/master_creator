


import requests
import common
import json
import copy
import time


'''
根据targeting计算人群规模
'''
def get_estimate_daily_result(targeting):

    jdata = {'targeting_spec': json.dumps(targeting),
             "optimization_goal": "OFFSITE_CONVERSIONS"
             }
    url = common.get_targeting_estimate_url()
    res = requests.get(url, params=jdata)
    out = json.loads(res.text)
    if 'data' in out and len(out['data']) and 'estimate_dau' in out['data'][0] and out['data'][0]['estimate_ready']:
        return out['data'][0]
    else:
        dict()


'''
计算同一个campaign下的重组的targeting和其他targeting的重合度
'''
def get_overlap_cmp(data, out_estimate):
    max_overlap = 0
    if not out_estimate or (isinstance(out_estimate, dict) and 'estimate_dau' not in out_estimate):
        return max_overlap
    if 'campaign_id' in data:
        url = common.get_campaign_adset_url(data['campaign_id'])
        targetings = list()
        while True:
            res_out = requests.get(url)
            out = json.loads(res_out.text)
            if 'data' in out:
                targetings.extend(out['data'])
            if 'paging' in out and 'next' in out['paging']:
                url = out['paging']['next']
            else:
                res_out.close()
                break
        for tar in targetings:
            if tar['id'] != data['id']:
                other = get_edaily_result(tar['id'])
                tmp_targeting = copy.deepcopy(tar['targeting'])
                targeting = copy.deepcopy(data['targeting'])
                if 'behaviors' in targeting and 'behaviors' in tmp_targeting:
                    tmp_targeting['behaviors'].extend(targeting['behaviors'])
                if 'interests' in targeting and 'interests' in tmp_targeting:
                    tmp_targeting['interests'].extend(targeting['interests'])
                together = get_estimate_daily_result(tmp_targeting)
                if out_estimate and other and together:
                    x1 = int(out_estimate['estimate_dau'])
                    x2 = int(other['estimate_dau'])
                    x3 = int(together['estimate_dau'])
                    estimate = abs(x1+x2-x3)/(x3+1)*100
                    if max_overlap < estimate <= 100:
                        max_overlap = estimate
        return max_overlap


'''
根据adset_id获取在线asset的人群规模
'''
def get_edaily_result(adset_id):
    index = 0
    while index < 3:
        res = requests.get(common.get_adset_estimate_url(adset_id))
        out = json.loads(res.text)
        if 'data' in out and len(out['data']) and 'estimate_dau' in out['data'][0] and out['data'][0]['estimate_ready']:
            return out['data'][0]
        index += 1
        time.sleep(1)
    return dict()

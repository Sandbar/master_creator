

import requests
import json
import common
import os

tindex = 0


'''
在指定adset_id下创建ad
'''
def create_ad(adset_id, group, platform, videos):
    global tindex
    video = videos[tindex % len(videos)]
    link = "http://play.google.com/store/apps/details?id=com.tap4fun.brutalage_test"
    if platform.lower() == 'ios' or 'ios' in platform.lower():
        link = "https://itunes.apple.com/app/id1156787368"
    json_data = {
        "name": common.get_name(group, platform),
        "adset_id": adset_id,
        "status": "ACTIVE",
        "creative": {
            "object_story_spec": {
                "page_id": "1643949305846284",
                "video_data": {
                    "video_id": video['videoid'],
                    "message": video['message'],
                    "call_to_action": {
                        "type": "INSTALL_MOBILE_APP",
                        "value": {
                            "application": "634204786734953",
                            "link": link
                        }
                    },
                    "image_url": video['image_url']
                }
            }
        },
        "access_token": os.environ['access_token']
    }
    res = requests.post(common.get_ad_url(), json=json_data)
    res.close()
    out = json.loads(res.text)
    tindex += 1
    if 'id' in out:
        return out['id']
    else:
        return None

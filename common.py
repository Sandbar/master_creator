

import mysql
import time
import os
import datetime

FB_URL = "https://graph.facebook.com/v3.1/"


def get_basic_data():
    basic_data = dict()
    basic_data['video'] = mysql.select_videos()
    basic_data['group'] = mysql.select_country_group()
    basic_data['object_store_url'] = {'ios': 'https://itunes.apple.com/app/id1156787368', 'android': 'http://play.google.com/store/apps/details?id=com.tap4fun.brutalage_test'}
    return basic_data


def get_adset_url():
    return FB_URL+'act_'+str(os.environ['accountid'])+'/adsets'


def get_adcreatives_url():
    return FB_URL+'act_'+str(os.environ['accountid'])+'/adcreatives'


def get_ad_url():
    return FB_URL+'act_'+str(os.environ['accountid'])+'/ads'


def get_del_adset_url(adset_id):
    return FB_URL+str(adset_id)+'?access_token='+os.environ['access_token']


def get_name(group, platform):
    return "{0} {1} {2} [{3}][archer]".format(group, platform, str(datetime.datetime.now().strftime('%Y-%m-%d')), int(round(time.time() * 1000))).upper()


def get_adaset_data_url(adset_id):
    return FB_URL + str(adset_id) + '?fields=name,bid_amount,daily_budget,bid_strategy,billing_event,attribution_spec,optimization_goal,promoted_object,targeting&access_token='+os.environ['access_token']


def get_campaign_data_url(campaign_id):
    return FB_URL+str(campaign_id)+'?fields=name,id,status,objective,buying_type,created_time&access_token='+os.environ['access_token']


def get_adset_estimate_url(adset_id):
    return FB_URL+str(adset_id)+'/delivery_estimate?fields=daily_outcomes_curve,estimate_dau,estimate_mau,estimate_ready&access_token='+os.environ['access_token']


def get_targeting_estimate_url():
    return FB_URL+'act_'+str(os.environ['accountid'])+'/delivery_estimate?access_token='+os.environ['access_token']


def get_campaign_adset_url(campaign_id):
    return FB_URL+str(campaign_id)+'/adsets?fields=id,targeting&limit=300&access_token='+os.environ['access_token']



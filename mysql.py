

import pymysql
import pandas as pd
import os
import requests
import json
from random import choice


def select_feature():
    conn = pymysql.connect(host=os.environ['mysql_db_host'], user=os.environ['mysql_db_user'],
                           password=os.environ['mysql_db_pwd'], db=os.environ['mysql_db_name'],
                           port=int(os.environ['mysql_db_port']))
    sql = '''SELECT id,	'behavior' as `type`,name  FROM ai_ad_targeting_prod_2.dw_dim_behavior UNION ALL SELECT id,	'interest' as `type`,name  FROM ai_ad_targeting_prod_2.dw_dim_interest_sample'''
    target_data = pd.read_sql(sql, conn)
    # print(target_data)
    tmp = dict()
    for index in range(len(target_data)):
        tmp[target_data.iloc[index]['id']] = {'name': target_data.iloc[index]['name'],
                                              'type': target_data.iloc[index]['type']
                                              }
    conn.close()
    return tmp


def select_videos():
    messages = ["Start your own brutal prehistoric adventure, come and join us now! ! ！⛺",
                "Be careful what you fish for in this barbarian world. Fight and fish for your Hordes survival.",
                "Experience What It is Like To Train And Fight a Horde of Barbarians in BRUTAL AGE.",
                "The Blue Horde is in trouble again, they need your help!",
                "The Blue Horde levelling up like a Brutal Age BOSS.",
                "Oh no!!..not again.",
                "Be The Hero Your Horde Needs, in BRUTAL AGE.",
                "Lead Your Horde To Victory, in BRUTAL AGE.",
                "The Blue Horde vs the Red Horde, who will win?",
                "We Were Looking For a Big One, But Not THAT Big.",
                "And you thought this game was only about fighting.",
                "Train and Fight Like a True Barbarian in BRUTAL AGE.",
                "Take Down Enemy Hordes And Conquer Their Land.",
                "In Brutal Age one must know when to fight, and when to retreat.",
                "Do What Ever It Takes To Protect Your Loot!",
                "Charge through the enemy, we will achieve victory!/nothing will stop us!",
                "Keep them coming, we’ll handle them all!!",
                "How to tame a mammoth - Brutal Age style.",
                "Taking down Mammoths is just all in a day’s work for the Blue Horde.",
                "Be The Chief of Your Horde, Join The Brutal Age Community Today!",
                "now that’s a pain in the butt!!",
                "Fight Till Your Last Man. Play Now For Free.",
                "a true barbarian can catch anything",
                "The Blue Horde has hobbies too you know...",
                "Meat Weapons and Spears, Experience Barbarian Battles in BRUTAL AGE.",
                "Take Down Enemy Hordes By Any Means Necessary.",
                "A reel good time.",
                "OMG!! I think we need a bigger net...",
                "Boulders, battles and massive beasts. THIS is Brutal Age."]
    fb_url = 'https://graph.facebook.com/v3.1/act_'+os.environ['accountid']+'/advideos?fields=thumbnails{uri},id&limit=1100&access_token='+os.environ['access_token']
    res = requests.get(fb_url)
    res_out = json.loads(res.text)["data"]
    res.close()
    tmp_videos = list()
    for tx in res_out:
        if 'id' in tx and 'thumbnails' in tx and 'data' in tx['thumbnails'] and len(tx['thumbnails']['data']):
            tmp_videos.append({'videoid': tx['id'], 'image_url': tx['thumbnails']['data'][0]['uri'], 'message': choice(messages)})
    return tmp_videos


def select_country_group():
    conn = pymysql.connect(host=os.environ['mysql_db_host'], user=os.environ['mysql_db_user'],
                           password=os.environ['mysql_db_pwd'], db=os.environ['mysql_db_name'],
                           port=int(os.environ['mysql_db_port']))
    sql = "SELECT distinct country,lower(`group`) as `group` FROM country"
    countries = pd.read_sql(sql, conn)
    country = dict()
    for index in range(len(countries)):
        row = countries.iloc[index]
        if row['group'] not in country:
            country[row['group']] = []
        country[row['group']].append(row['country'])
    conn.close()
    return country

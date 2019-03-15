

import mysql
import fp_growth as fpg
import time
import random
import mongo
import copy
import common
import adsets_creator
import ad_creator
import get_adset_estimate
import os
import log_maker

class Archer_Update():
    def __init__(self):
        self._good_combo = dict()
        self._bad_combo = dict()
        self._temporary_list = list()
        self.all_attrivutes = dict()
        self._good_dict = dict()
        self._bad_dict = dict()
        self._is_OK = False

    '''
    获取targetings并计算频繁项集，过滤掉小于minimum_support的部分，num_combo表示兴趣、行为组合的个数
    '''
    def calc_fp_growth(self, attrivute_list, minimum_support=2, num_combo=2):
        result = dict()
        tmp_dict = dict()
        if len(attrivute_list) > 0:
            frequent_itemsets = fpg.find_frequent_itemsets(attrivute_list, minimum_support, include_support=True)
            for itemset, support in frequent_itemsets:
                if len(itemset) == num_combo:
                    if itemset[0] > itemset[1]:
                        tname = itemset[1]+'_'+itemset[0]
                    else:
                        tname = itemset[0]+'_'+itemset[1]
                    if itemset[0] not in tmp_dict:
                        tmp_dict[itemset[0]] = []
                    tmp_dict[itemset[0]].append(tname)
                    if itemset[1] not in tmp_dict:
                        tmp_dict[itemset[1]] = []
                    tmp_dict[itemset[1]].append(tname)
                    result[tname] = support
        return result, tmp_dict

    '''
    将targeting中的兴趣和行为进行合并并返回list
    '''
    def decompose_targeting(self, targeting):
        if 'flexible_spec' in targeting:
            for attr in targeting['flexible_spec']:
                if 'interests' in attr:
                    targeting['interests'] = copy.deepcopy(attr['interests'])
                elif 'behaviors' in attr:
                    targeting['behaviors'] = copy.deepcopy(attr['behaviors'])
        if 'flexible_spec' in targeting:
            del targeting['flexible_spec']
        tmp_list = list()
        if 'interests' in targeting:
            interests = targeting['interests']
            if isinstance(interests, list):
                for interest in interests:
                    if isinstance(interest, dict) and 'id' in interest:
                        tmp_list.append(str(interest['id']).replace('.0', ''))
                    elif isinstance(interest, str) or isinstance(interest, float) or isinstance(interest, int):
                        tmp_list.append(str(interest).replace('.0', ''))

            elif isinstance(interests, dict):
                for interest in interests.values():
                    tmp_list.append(str(interest['id']).replace('.0', ''))

        if 'behaviors' in targeting:
            behaviors = targeting['behaviors']
            if isinstance(behaviors, list):
                for behavior in behaviors:
                    if isinstance(behavior, dict):
                        tmp_list.append(str(behavior['id']).replace('.0', ''))
                    elif isinstance(behavior, str) or isinstance(behavior, float) or isinstance(behavior, int):
                        tmp_list.append(str(behavior).replace('.0', ''))
            elif isinstance(behaviors, dict):
                for behavior in behaviors.values():
                    if 'id' in behavior:
                        tmp_list.append(str(behavior['id']).replace('.0', ''))
        return tmp_list

    '''
    将读取的兴趣和行为进行划分
    '''
    def waiting_attribute(self, tmp_list):
        behaviors = list()
        interests = list()
        for vid in self._temporary_list:
            if self.all_attrivute[vid]['type'] == 'behavior' and vid not in tmp_list:
                behaviors.append(vid)
            elif self.all_attrivute[vid]['type'] == 'interest' and vid not in tmp_list:
                interests.append(vid)
        return behaviors, interests

    '''
    随机选择一个无法识别的兴趣行为进行替换
    '''
    def random_replace(self, targeting, interests, behaviors):
         if 'interests' in targeting and len(targeting['interests']) > 0 and len(interests) > 0:
             choice_index = random.randint(0, len(targeting['interests'])-1)
             tid = random.choice(interests)
             targeting['interests'][choice_index] = {'id': tid, 'name': self.all_attrivute[tid]['name']}
         if 'behaviors' in targeting and len(targeting['behaviors']) > 0 and len(behaviors) > 0:
             choice_index = random.randint(0, len(targeting['behaviors'])-1)
             tid = random.choice(behaviors)
             targeting['behaviors'][choice_index] = {'id': tid, 'name': self.all_attrivute[tid]['name']}
         return targeting

    '''
    通过重组的targeting进行adset和ad创建
    '''
    def rebuild_adset(self, data):
        tn = data['name'].split(' ')
        if len(tn) < 2 and 'id' in data:
            return data['id']
        if tn[1] in 'US_T1OTHER_ME_ROW' and tn[0] in 'ANDROID_IOS':
            tn[1], tn[0] = tn[0], tn[1]
        basic_data = common.get_basic_data()
        adset_id = adsets_creator.create_adset(data, tn[0], tn[1], basic_data)
        if adset_id:
            for _ in range(int(os.environ['ad_size'])):
                sign = True
                tmindex = 0
                while sign:
                    tmindex += 1
                    if tmindex >= 4:
                        sign = False
                        break
                    try:
                        ad_id = ad_creator.create_ad(adset_id, tn[0], tn[1], basic_data['video'])
                        if ad_id:
                            sign = False
                    except Exception as e:
                        time.sleep(1)
            adsets_creator.del_adset(data['id'], 0)
            adset_data = adsets_creator.get_adset_data(adset_id)
            mongo.update_adsets(str(data['id']), str(adset_id), adset_data)
        if adset_id:
            return adset_id
        else:
            time.sleep(2)
            return self.rebuild_adset(data)
    '''
    targeting重组，产生新的满足条件，如果重复5次不能满足所有条件，则选择5次中最好的一次进行创建adset 
    '''
    def update_targeting(self, data, tmax_index=0, tm_data=None):
        if 'targeting' not in data and 'id' in data:
            return data['id']
        if tmax_index > 5:
            if tm_data and (isinstance(tm_data, dict) and 'data' in tm_data):
                return self.rebuild_adset(tm_data['data'])
            else:
                return data['id']

        targeting = data['targeting']
        if 'flexible_spec' in targeting:
            for attr in targeting['flexible_spec']:
                if 'interests' in attr:
                    targeting['interests'] = copy.deepcopy(attr['interests'])
                elif 'behaviors' in attr:
                    targeting['behaviors'] = copy.deepcopy(attr['behaviors'])
            del targeting['flexible_spec']
        stop_index = 0
        while not self._is_OK or stop_index > 50:
            stop_index += stop_index
            time.sleep(3)
        if self._is_OK:
            del_lst = []
            add_lst = []
            tmp_list = self.decompose_targeting(targeting)
            for tid in tmp_list:
                if tid in self._bad_dict:
                    del_lst.append(tid)
                if tid in self._good_dict:
                    add_lst.append(tid)
            behaviors, interests = self.waiting_attribute(tmp_list)
            if len(del_lst) == 0 and len(add_lst) == 0:
                targeting = self.random_replace(targeting, interests, behaviors)
            else:
                good_attributes = list()
                for tdid in tmp_list:
                    good_attributes.extend(self._good_dict.get(tdid, []))
                interest_sign = False
                behavior_sign = False
                if len(good_attributes) > 0:
                    random.shuffle(good_attributes)
                    for arrribute in good_attributes:
                        tmpid = arrribute.split('_')
                        if len(tmpid) == 2:
                            tmp = self.all_attrivute.get(tmpid[1], None)
                            if tmpid[1] not in tmp_list:
                                if tmp['type'] == 'interest' and not interest_sign:
                                    targeting['interests'].append({'id': tmpid[1], 'name': tmp['name']})
                                    interest_sign = True
                                elif tmp['type'] == 'behavior' and not behavior_sign:
                                    targeting['behaviors'].append({'id': tmpid[1], 'name': tmp['name']})
                                    behavior_sign = True
                        if interest_sign and behavior_sign:
                            break
                if not interest_sign and 'interests' in targeting and isinstance(targeting['interests'], list) and len(interests) > 0:
                    tid = random.choice(interests)
                    targeting['interests'].append({'id': tid, 'name': self.all_attrivute[tid]['name']})
                if not behavior_sign and 'behaviors' in targeting and isinstance(targeting['behaviors'], list) and len(behaviors) > 0:
                    tid = random.choice(behaviors)
                    targeting['behaviors'].append({'id': tid, 'name': self.all_attrivute[tid]['name']})
                if len(self._bad_dict) > 0:
                    interest_sign0 = False
                    behavior_sign0 = False
                    kvids = random.shuffle(list(self._bad_dict.keys()))
                    if kvids and len(kvids) > 0:
                        for kvid in kvids:
                            if kvid in tmp_list:
                                tmp_attr = self.all_attrivute[kvid]
                                tattr = {'id': tmp_attr['id'], 'name': tmp_attr['name']}
                                if not interest_sign0 and 'interests' in targeting and tattr in targeting['interests']:
                                    targeting['interests'].remove(tattr)
                                    interest_sign0 = True
                                if not behavior_sign0 and 'behaviors' in targeting and tattr in targeting['behaviors']:
                                    targeting['behaviors'].remove(tattr)
                                    behavior_sign0 = True
                            if interest_sign0 and behavior_sign0:
                                break
            data['targeting'] = copy.deepcopy(targeting)
            out_estimate = get_adset_estimate.get_estimate_daily_result(data['targeting'])
            if not out_estimate:
                return self.update_targeting(data, tmax_index+1, tm_data)
            overlap = get_adset_estimate.get_overlap_cmp(data, out_estimate)
            if tm_data is None:
                tm_data = {'data': data, 'overlap': overlap}
            if overlap <= int(os.environ['overlap']) and 'estimate_dau' in out_estimate:
                if int(os.environ['min_dau']) <= out_estimate['estimate_dau'] <= int(os.environ['max_dau']):
                    return self.rebuild_adset(data)
                elif ('overlap' not in tm_data) or ('estimate_dau' in tm_data and tm_data['overlap'] > overlap):
                    tm_data = {'data': data, 'overlap': overlap}
            return self.update_targeting(data, tmax_index+1, tm_data)
        else:
            return data['id']

    '''
    加载数据，并通过fp-growth算法生成频繁项树
    '''
    def load_ads_update_model(self):
        targetings = mongo.get_ads_targetings()
        good_ids_lst = list()
        bad_ids_lst = list()
        log_maker.root.info('entry into fp-growth')
        for targeting in targetings:
            if 'true' in str(targeting['is_good']):
                good_ids_lst.append(self.decompose_targeting(targeting['targeting']))
            else:
                bad_ids_lst.append(self.decompose_targeting(targeting['targeting']))
        log_maker.root.info(('the size of good %s' % str(len(good_ids_lst))))
        tgood_combo, tgood_dict = self.update_model(good_ids_lst, is_good=True)
        log_maker.root.info(('the size of bad %s' % str(len(bad_ids_lst))))
        tbad_combo, tbad_dict = self.update_model(bad_ids_lst, is_good=False)
        self._is_OK = False
        self._good_combo = copy.deepcopy(tgood_combo)
        self._good_dict = copy.deepcopy(tgood_dict)
        self._bad_combo = copy.deepcopy(tbad_combo)
        self._bad_dict = copy.deepcopy(tbad_dict)
        self.all_attrivute = mysql.select_feature()
        self._temporary_list = list(self.all_attrivute.keys())
        if len(self._good_dict) > 0 or len(self._bad_combo) > 0:
            for index in range(len(self._temporary_list)-1, -1, -1):
                if self._temporary_list[index] in self._good_dict or self._temporary_list[index] in self._bad_dict:
                    self._temporary_list.pop(index)
        self._is_OK = True

    '''
    评价好的targeting和不好targeting分别通过fp-growth算法进行创建频繁项集
    '''
    def update_model(self, ids_lst, is_good=True):
        minimum_support = 2
        try:
            minimum_support = int(os.environ['minimum_support'])
        except:
            minimum_support = 2
        if is_good:
            tgood_combo, tgood_dict = self.calc_fp_growth(ids_lst, minimum_support=minimum_support)
            for index in range(len(self._temporary_list)-1, -1, -1):
                if self._temporary_list[index] in self._good_dict.keys():
                    self._temporary_list.pop(index)
            return tgood_combo, tgood_dict
        else:
            tbad_combo, tbad_dict = self.calc_fp_growth(ids_lst, minimum_support=minimum_support)
            for index in range(len(self._temporary_list)-1, -1, -1):
                if self._temporary_list[index] in self._bad_dict.keys():
                    self._temporary_list.pop(index)
            return tbad_combo, tbad_dict

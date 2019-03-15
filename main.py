

from flask import Flask, request
import master
import os
import json
import time
import log_maker


app = Flask(__name__)


mrau = master.Archer_Update()
is_waiting = False


@app.route('/update_model', methods=['GET'])
def update_model():
    try:
        if request.method == 'GET':
            log_maker.root.info("waiting,updating model...")
            mrau.load_ads_update_model()
            log_maker.root.info('work done')
            return "OK, model updated..."
        else:
            log_maker.root.error('failure')
            return "failure"
    except Exception as e:
        log_maker.root.error(str(e))
        return "except"


@app.route('/update_targeting', methods=['GET', 'POST'])
def update_targeting():
    try:
        if request.method == 'POST':
            data = json.loads(request.get_data())
            if isinstance(data,dict) and 'id' in data:
                log_maker.root.info('received %s' % (str(data['id'])))
            global is_waiting
            while is_waiting:
                time.sleep(5)
            is_waiting = True
            adset_id = mrau.update_targeting(data)
            log_maker.root.info('replace %s -> %s' % (str(data['id']), str(adset_id)))
            is_waiting = False
            return json.dumps({'adset_id': adset_id})
        else:
            is_waiting = False
            return "GET Request"
    except Exception as e:
        log_maker.root.error(str(e))
        is_waiting = False
        return "except"


app.run('0.0.0.0', int(os.environ['tm_port']))


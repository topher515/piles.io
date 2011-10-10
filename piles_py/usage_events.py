from celery import events
from db import db
from datetime import datetime

def usage_put_handler(log):
    # Do storage calc updates
    current = db.storage_totals.save({'_id':log['pid'], 'size':{'$inc':int(log['size'])}})
    db.storage_ref.save({'pid':current['_id'], 'size':int(current['size']), 'at_time':log['logged_time']})
    # Save event
    db.usage_events.save(log)
    
    
def usage_get_handler(log):
    # Save event
    db.usage_events.save(log)


def usage_del_handler(log):
    # Do storage calc updates
    current = db.storage_totals.save({'_id':log['pid'], 'size':{'$inc':-int(log['size'])}})
    db.storage_ref.save({'pid':current['_id'], 'size':int(current['size']), 'at_time':log['logged_time']})
    # Save event
    db.usage_events.save(log)


def storage_eval_handler(spec):
    # Spec should have 'pid' in it
    current = db.storage_totals.find(spec)
    db.storage_ref.save({'pid':current['_id'], 'size':int(current['size']), 'at_time':log['logged_time']})


event_receiver = events.EventReceiver(handlers={

    'usage.put':usage_put_handler,
    'usage.get':usage_get_handler,
    'usage.del':usage_del_handler,
    'storage.eval':storage_eval_handler,

})
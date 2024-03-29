from contentstore import S3Store
import json
import pymongo
from db import db
import apachelog
from datetime import datetime, timedelta
import logging
logger = logging.getLogger()
from utils import FakeLogger
logger = FakeLogger()

from settings import settings #LOG_BUCKET, LOG_BUCKET_PREFIX # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


#from celery import registry, task, events
#event_dispatcher = events.EventDispatcher()



class UsageMeter(object):
    ''' Map/Reduce Amazon S3 log information to extract PUT/GET
    usage information.
    '''
    def __init__(self,custom={}):
        # The default settings for cost, etc.
        self.defaults = {
            # Storage
            "storage_cost": 0.16,           # in dollars/gigabyte/month
            # Usage get
            "usage_get_cost": 0.14,         # in dollars/gigabyte
            # Usage put
            "usage_put_cost": 0.02,         # in dollars/gigabyte
            # Freeloaders
            'freeloaders_this_month_dollars': 0.25, # in dollars
        }
        
        # Zero out all of the important values
        self.defaults.update({
            # Storage
            "storage_current_bytes": 0,     # in bytes
            "storage_total_byte_hours": 0,  # in byte-hours
            "storage_total_dollars":0,           
            "storage_this_month_byte_hours": 0, # in byte-hours
            "storage_this_month_dollars":0,

            # Usage get
            "usage_get_total_bytes": 0,     # in bytes
            "usage_get_total_dollars": 0,
            'usage_get_this_month_bytes':0, # in bytes
            "usage_get_this_month_dollars":0,

            # Usage put
            "usage_put_total_bytes": 0,     # in bytes
            'usage_put_total_dollars':0,    
            'usage_put_this_month_bytes':0, # in bytes
            "usage_put_this_month_dollars":0,

            # Summary
            'total_dollars':0,
            'this_month_dollars':0,
        })
        
        self.defaults.update(custom)
    
        
    
    def update(self):
        self._mr_storage_totals()
        self._mr_storage_dailies()
        self._mr_storage_monthlies()
        self._mr_usage_totals()
        self._mr_usage_dailies()
        self._mr_usage_monthlies()
    
    
    def over_limit(self,pid):
        summary = self.summary(pid)        
        return summary['this_month_dollars'] > summary['freeloaders_this_month_dollars']

    
    
    def summary(self,pid):
        
        now = datetime.now()
        
        summary = dict(self.defaults)

        ### Gather byte data
        # Storage current
        s = db.storage_totals.find_one({'value.pid':pid})
        summary['storage_current_bytes'] = s['value']['size'] if s else 0
        
        
        # Calculate byte-hours from dailies
        try:
            sto_dailies = db.storage_dailies.find({'value.pid':pid})
            prev_date = sto_dailies.next()
            a_day_later = {'value':{'date':prev_date['value']['date'] + timedelta(days=1),'size':0}}
            next_date = sto_dailies.next()
            cur_bytes = 0
        except StopIteration:
            logger.warn("Not enough data to calculate summary")
            return summary
            
        while True:
            
            # Choose time interval
            if (next_date['value']['date'] - prev_date['value']['date']) < timedelta(days=2):
                # If the next date is less than two days then use it
                closer_date = next_date
                try:
                    next_date = sto_dailies.next()
                except StopIteration:
                    break
            else:
                # Otherwise use `the next day`
                closer_date = a_day_later
            a_day_later = {'value':{'date':prev_date['value']['date'] + timedelta(days=1),'size':0}}
            
            # Sum bytes
            cur_bytes += prev_date['value']['size']
            
            cd = closer_date['value']['date']
            
            # Calculate byte hours for this time frame
            timepassed = closer_date['value']['date'] - prev_date['value']['date']
            secspassed = timepassed.days * 3600*24 + timepassed.seconds
            byte_secs = secspassed * cur_bytes
            byte_hours = byte_secs / 3600
            
            # If we're looking at a date in *the current month* 
            # then add this sum to the current month 
            if cd.year == now.year and cd.month == now.month:
                summary['storage_this_month_byte_hours'] += byte_hours
            summary['storage_total_byte_hours'] += byte_hours
            
            # Overwrite prev_date to continue the loop
            prev_date = closer_date
        
        # Usage totals
        for ut in db.usage_totals.find({'value.pid':pid}):
            if ut['value']['op'] == 'PUT':
                summary['usage_put_total_bytes'] = ut['value']['size']
            elif ut['value']['op'] == 'GET':
                summary['usage_get_total_bytes'] = ut['value']['size']
        # Usage this month
        for utm in db.usage_monthlies.find({'value.pid':pid}, sort=[('date',pymongo.DESCENDING)]):
            if utm['value']['op'] == 'PUT':
                summary['usage_put_this_month_bytes'] = utm['value']['size']
            elif utm['value']['op'] == 'GET':
                summary['usage_get_this_month_bytes'] = utm['value']['size']
               
                
        # Calculate costs
        # Convert from bytes to gigabytes divide by 1024 three times
        # convert from hours to months divide by 730.484398 (hours in a month)
        summary['storage_total_dollars'] = summary['storage_total_byte_hours'] * summary['storage_cost'] / (1024*1024*1024) / (730.484398)
        summary['storage_this_month_dollars'] = summary['storage_this_month_byte_hours'] * summary['storage_cost'] / (1024*1024*1024) / (730.484398)
        
        # Convert from bytes to gigabytes by dividing by 1024 three times
        summary['usage_put_total_dollars'] = summary['usage_put_total_bytes'] * summary['usage_put_cost'] / (1024*1024*1024) 
        summary['usage_get_total_dollars'] = summary['usage_get_total_bytes'] * summary['usage_get_cost'] / (1024*1024*1024)
        summary['usage_put_this_month_dollars'] = summary['usage_put_this_month_bytes'] * summary['usage_put_cost'] / (1024*1024*1024) 
        summary['usage_get_this_month_dollars'] = summary['usage_get_this_month_bytes'] * summary['usage_get_cost'] / (1024*1024*1024)
        
        summary['total_dollars'] = summary['usage_put_total_dollars'] + \
            summary['usage_get_total_dollars'] + summary['storage_total_dollars']
        summary['this_month_dollars'] = summary['usage_put_this_month_dollars'] + \
            summary['usage_get_this_month_dollars'] + summary['storage_this_month_dollars']
        
        return summary
    
    
        
    def usage_total(self,pid,op=None):
        '''Return the dict representing the total usage by op type (GET,PUT,DELETE) for the `pid`'''
        spec = {'value.pid':pid}
        if op:
            spec['value.op'] = op
        r=(db.usage_totals.find_one(spec) or {'value':None})['value']
        logger.debug('usage total %s' % r)
        return r
        
    def storage_dailies(self,pid):
        r=[s['value'] for s in (db.storage_dailies.find({'value.pid':pid}) or [])]
        
        
        logger.debug('Storage dailies %s' % r)
        return r
                 
        
    def usage_dailies(self,pid):
        r=[s['value'] for s in (db.usage_dailies.find({'value.pid':pid}) or [])]
        
        '''
        dailies = []
        
        dayiter = iter(r)
        prevday = dayiter.next()
        dailies.append(prevday)
        curday = prevday['da
        while curday:
            dailies.append(curday)
            daydelta = (curday['date'] - prevday['date'])
            if daydelta >= timedelta(days=2):
                prevday = curday
                curday = {
                    'size':0,
                    'date':curday['date']+timedelta(days=1)
                }
            else:
                prevday = curday
                try:
                    curday = dayiter.next()
                except StopIteration:
                    break
        '''
        
        return r
        
    def storage_monthlies(self,pid):
        r=[s['value'] for s in (db.storage_monthlies.find({'value.pid':pid}) or [])]
        logger.debug('Storage monthlies %s' % r)
        return r

    def usage_monthlies(self,pid):
        r=[s['value'] for s in (db.usage_monthlies.find({'value.pid':pid}) or [])]
        logger.debug('Usage monthlies %s' % r)
        return r

    def usage_this_month(self,pid,op)  :
        m = db.usage_monthlies.find({'value.pid':pid,'value.op':op}, sort=[('date',pymongo.DESCENDING)])
        if m and m.count() > 0:
            return m[0]
        return None
   
    
    def reset(self):
        for c in ['storage_totals','storage_dailies','usage_totals','usage_dailies', 'storage_monthlies','usage_monthlies']:
            db.mr_tracker.remove({'collection':c})
            db[c].remove({})
    
    
    def _mr_usage_monthlies(self):

        map_func ='''function() {
                    var themonth = new ISODate()
                    themonth.setFullYear(this.logged_time.getFullYear(), this.logged_time.getMonth());
                    emit( this.pid + ':' + this.op + ':' + themonth.toDateString(),
                        {size: Number(this.size), date: this.logged_time, pid: this.pid, op: this.op});
                }'''
        reduce_func = '''function(key,values) {
                    var result = {size: 0}
                    values.forEach(function(value) {
                        result.size += value.size;
                        result.date = value.date;
                        result.pid = value.pid;
                        result.op = value.op;
                    });
                    return result;
                }'''

        return self._do_mr(map_func,reduce_func,'usage_events','usage_monthlies')
    
    
    def _mr_storage_totals(self):
        
        map_func = '''function() {
                    if (this.op == 'PUT') {
                        emit(this.pid, { pid: this.pid, size: Number(this.size) })
                    } else if (this.op == 'DELETE') {
                        emit(this.pid, { pid: this.pid, size: -Number(this.size) })
                    }
                }'''
        reduce_func = '''function(key,values) {
                    var result = {
                        size: 0,
                        pid: '',
                    }
                    values.forEach(function(val) {
                        result.size += val.size;
                        result.pid = val.pid;
                    });
                    return result;
                }'''
      
        return self._do_mr(map_func,reduce_func,'usage_events','storage_totals')  


    def _mr_storage_monthlies(self):

        map_func = '''function() {

                    var date = new ISODate()
                    date.setFullYear(this.logged_time.getFullYear(),this.logged_time.getMonth())

                    if (this.op == 'PUT') {
                        emit(this.pid + ':' + date.toDateString(), 
                            { pid: this.pid, 
                            size: Number(this.size),
                            date:this.logged_time,
                        })

                    } else if (this.op == 'DELETE') {
                        emit(this.pid + ':' + date.toDateString(),
                            { pid: this.pid, 
                            size: -Number(this.size),
                            date: this.logged_time,
                        })
                    }
                }'''
        reduce_func = '''function(key,values) {
                    var result = {
                        size: 0,
                        pid: '',
                        date: null,
                    }
                    values.forEach(function(val) {
                        result.size += val.size;
                        result.pid = val.pid;
                        result.date = val.date
                    });
                    return result;
                }'''

        return self._do_mr(map_func,reduce_func,'usage_events','storage_monthlies')

    
    def _mr_storage_dailies(self):

        map_func = '''function() {
                
                    var date = new ISODate()
                    date.setFullYear(this.logged_time.getFullYear(),this.logged_time.getMonth(),this.logged_time.getDate())
                    
                    if (this.op == 'PUT') {
                        emit(this.pid + ':' + date.toDateString(), 
                            { pid: this.pid, 
                            size: Number(this.size),
                            date:this.logged_time,
                        })
                            
                    } else if (this.op == 'DELETE') {
                        emit(this.pid + ':' + date.toDateString(),
                            { pid: this.pid, 
                            size: -Number(this.size),
                            date: this.logged_time,
                        })
                    }
                }'''
        reduce_func = '''function(key,values) {
                    var result = {
                        size: 0,
                        pid: '',
                        date: null,
                    }
                    values.forEach(function(val) {
                        result.size += val.size;
                        result.pid = val.pid;
                        result.date = val.date
                    });
                    return result;
                }'''

        return self._do_mr(map_func,reduce_func,'usage_events','storage_dailies')    
    
    
    def _mr_usage_totals(self):

        map_func = '''function() {
                    emit(this.pid + ':' + this.op, 
                        {
                            size: Number(this.size),
                            pid: this.pid,
                            op: this.op
                        }
                    )
                }'''
        reduce_func = '''function(key,values) {
                    var result = {size: 0, pid:''}
                    values.forEach(function(value) {
                        result.size += value.size;
                        result.pid = value.pid;
                        result.op = value.op;
                    });
                    return result;
                }'''

        return self._do_mr(map_func,reduce_func,'usage_events','usage_totals')



    def _mr_usage_dailies(self):
        
        map_func ='''function() {
                    var theday = new ISODate()
                    theday.setFullYear(this.logged_time.getFullYear(), this.logged_time.getMonth(), this.logged_time.getDate());
                    emit( this.pid + ':' + this.op + ':' + theday.toDateString(),
                        {size: Number(this.size), date: this.logged_time, pid: this.pid, op: this.op});
                }'''
        reduce_func = '''function(key,values) {
                    var result = {size: 0}
                    values.forEach(function(value) {
                        result.size += value.size;
                        result.date = value.date;
                        result.pid = value.pid;
                        result.op = value.op;
                    });
                    return result;
                }'''

        return self._do_mr(map_func,reduce_func,'usage_events','usage_dailies')


    def _do_mr(self,map_func,reduce_func, mr_collection, res_collection):
        now = datetime.now()
        d = db.mr_tracker.find_one({'collection':res_collection}) or {}
        if d:
            print "Map-reduce the '%s' collection to '%s' after %s." % (mr_collection,res_collection, d['mr_time'])
            q = {'saved_time':{'$gt':d['mr_time']}}
            res =db[mr_collection].map_reduce(map=map_func,reduce=reduce_func,out={'reduce':res_collection},query=q)

        else:
            print "Map-reduce the '%s' collection to '%s' from start." % (mr_collection,res_collection)
            q = {}
            res = db[mr_collection].map_reduce(map=map_func,reduce=reduce_func,out={'replace':res_collection},query=q)
            
        d.update({'collection':res_collection,'mr_time':now})
        db.mr_tracker.save(d)
        return res

        


#@task.task
class S3LogParser(object): #task.Task):
    '''Parser for S3 access logs.
    '''
    
    def __init__(self):
        self.format = r'%{owner}i %{bucket}i %{datetime}t %{ip}h %{requester}i %{requestid}i %{operation}i %{key}i \"%{requesturi}i\" %{status}s %{error}i %{bytes}b %{objectsize}i %{totaltime}i %{turnaround}i \"%{referer}i\" \"%{useragent}i\" %{versionid}i'
        self.parser = apachelog.parser(self.format)

        self.log_mapper = {
            #'%{owner}i':('owner',None),
            '%{datetime}t':('logged_time',lambda dtstr: datetime.strptime(dtstr[:-6].strip('[]'),'%d/%b/%Y:%H:%M:%S ')),
            '%{ip}h':('ip',None),
            '%{requestid}i':('request_id',None),
            '%{operation}i':('operation',None),
            '%{key}i':('key',None),
            '%{requesturi}i':('uri',None),
            '%{requestid}i':('_id',None),
            '%{status}s':('status',int),
            '%{error}i':('error',None),
            '%{bytes}b':('bytes',int),
            '%{versionid}i':('version_id',None),
            '%{objectsize}i':('object_size',int)
        }


    def run(self,lines):
        return [self.parseline(l) for l in lines]

    def parseline(self,line):
        if not line:
            logger.warn('Skip parsing blank line!')
            return
        #logger.debug("Parsing line: %s" % line)
        parsed = self.parser.parse(line)
        ezlog = {}
        for key,(new_key,op) in self.log_mapper.iteritems():
            # Special case requesturi           
            val = parsed[key]
            if val == '-':
                ezlog[new_key] = None
            else:
                if op:
                    ezlog[new_key] = op(val)
                else:
                    ezlog[new_key] = val
        
        return ezlog
#s3_log_parse = registry.tasks[S3LogParser.name]


class S3LogGrabber(object):
    '''Provides iterator access to S3 access logs
    '''
    
    def __init__(self,log_bucket, log_prefix, max_keys=10000):
        self.bucket = log_bucket
        self.s3store = S3Store(bucket=self.bucket)
        self.prefix = log_prefix
        self.max_keys = max_keys
        self.cur_marker_key = None
        
    def logiter(self,marker=''):
        #beginstr = begin.strftime('%Y-%m-%d-%H-%M-%S')
        #endstr = end.strftime('%Y-%m-%d-%H-%M-%S')
        #ptr = 0
        #while beginstr[ptr] == endstr[ptr]:
        #   ptr+=1
        #dateprefix = beginstr[:prt]
        log_prefix = self.prefix #+ dateprefix
        options = {'Prefix':log_prefix,'MaxKeys':self.max_keys}
        if marker:
            options['marker'] = marker
            
        def fetchlogiter(listed):
            #logger.debug("Processing listed: %s --> %s" % (listed,listed.entries))
            for l in listed.entries:
                # Grab this 
                logger.debug("Getting object: %s" % l.key )
                logobj = self.s3store.get(l.key)
                for logline in logobj.body.split('\n'):
                    if not logline:
                        continue
                    #logger.debug("Logline: " + logline)
                    yield logline
                # We do this afterwards so that only finished processing
                # logs are marked
                self.cur_marker_key = l.key 
            
        listed = self.s3store.list_bucket(options)
        for line in fetchlogiter(listed):
            yield line
        while listed.is_truncated:
            for line in fetchlogiter(listed):
                yield line
            listed = self.s3store.list_bucket(options)


class S3LogProcessor(object):
    '''Grabs and processes (parses and saves in MongoDB) S3 access logs.
    Keeps track of last accessed log entry to prevent duplicate logging information 
    (last used log entry info is stored in MongoDB).
    '''
    
    def __init__(self,log_bucket, log_prefix, mongodb): 
        self.bucket = log_bucket
        self.prefix = log_prefix
        self.db = mongodb
        self.log_grabber = S3LogGrabber(self.bucket,self.prefix)
        self.log_parser = S3LogParser()

    def reset_log_marker(self):
        '''Forget the log marker
        '''
        self.db.log_processor.remove({'_id':'last-successful-log'})

    def _get_last_successful_log(self):
        l = self.db.log_processor.find_one({'_id':'last-successful-log'})
        return l['key'] if l else None
    def _set_last_successful_log(self,key):
        if key:
            logger.debug("Saving position in logs as... %s" % key)
            self.db.log_processor.save({'_id':'last-successful-log','key':key})
    last_successful_log = property(_get_last_successful_log, _set_last_successful_log, doc='''
        Keep track of the lastlog key which was successfully analyzed
    ''')



    def process_new_logs(self):
        '''Starting at the `last_successful_log` key, grab the latest
        Amazon logging data, normalize it and save it in the database.
        '''
        
        db = self.db
        
        def normalize_log(plogline):
            ''' Normalize Amazon Logs into format for our DB
            '''
            
            # Pull out PileID and FileID data
            s3key = plogline['key']
            index1 = s3key.index('/')
            pid = s3key[:index1]
            if pid == 'static':
                raise ValueError # This is actually just a static-file request
            remaining = s3key[index1+1:]
            index2 = remaining.index('/')
            fid = remaining[:index2]
            plogline['pid'] = pid
            plogline['fid'] = fid
            
            # Pull out file name data
            plogline['name'] = remaining[index2+1:]
            
            # Add current time
            plogline['saved_time'] = datetime.now()
            
            plogline['op'] = {
                'REST.GET.OBJECT':'GET',
                'REST.POST.BUCKET':'PUT',
                'REST.PUT.OBJECT':'PUT',
                'REST.DELETE.OBJECT':'DELETE'
            }[plogline['operation']]
                
            plogline['size'] = plogline['bytes'] or plogline['object_size']
            
            
            return plogline
        
        
        marker_key = self.last_successful_log
        logger.debug("Starting log process at marker: %s " % marker_key)
        
        plogline = None # We'll want to track this to save for later
        examined_count = 0 # The number of log lines examined
        processed_count = 0 # The number of log lines processed
        
        try: # If this dies for any reason we'll want to save our position
            
            interesting_ops = set(['REST.GET.OBJECT','REST.POST.BUCKET',\
                'REST.PUT.OBJECT','REST.DELETE.OBJECT'])
            
            for logline in self.log_grabber.logiter(marker_key):
                
                # Looking at a log line
                examined_count += 1
                
                if not logline:
                     # Got a blank line--just skip it
                    continue
                
                # Parse the logline
                plogline = self.log_parser.parseline(logline)
            
                if plogline['operation'] not in interesting_ops:
                    continue
                    
                try:
                    plogline = normalize_log(plogline)
                except ValueError:    
                    # This couldn't be normalized, so it's a 'system' op, IGNORE!
                    continue
                
                #event_dispatcher.send('usage.%s' % plogline['op'], log=plogline)
                db.usage_events.save(plogline)
 
                # We've successfully processed this logline!
                processed_count += 1
            
            
                continue # Ignore the cruft after here for now 
            
                ###
                ### GET operation (downloads)
                ###
                if plogline['operation'] == 'REST.GET.OBJECT':
                    try:
                        plogline = normalize_log(plogline)
                    except ValueError:
                        # This couldn't be normalized, so it's a 'system GET'
                        continue 
                        
                    #db.piles.update({'_id':plogline['pid']},{'$inc':{'usage_get':plogline['bytes']}})
                    db.usage_get_events.save(plogline)
                    
                ###
                ### PUT/POST operation (uploads)
                ###                
                elif plogline['operation'] == 'REST.POST.BUCKET' or plogline['operation'] == 'REST.PUT.OBJECT': # The put should never happen... but...
                    try:
                        plogline = normalize_log(plogline)
                    except ValueError:
                        # This couldn't be normalized, so it's a 'system GET'
                        continue
                        
                    #db.piles.update({'_id':plogline['pid']},{'$inc':{'usage_put':plogline['object_size'],'usage_sto':plogline['object_size']}})
                    db.usage_put_events.save(plogline)
                
                ###
                ### DELETE operation
                ###
                elif plogline['operation'] == 'REST.DELETE.OBJECT':
                    try:
                        plogline = normalize_log(plogline)
                    except ValueError:
                        # This couldn't be normalized, so it's a 'system GET'
                        continue 
                    
                    db.piles.update({'_id':plogline['pid']},{'$inc':{'usage_sto':-plogline['object_size']}})
                    db.usage_del_events.save(plogline)

                
                
        finally:
            # We'll want to save our place even if this dies for some reason
            self.last_successful_log = self.log_grabber.cur_marker_key
            print "Examined %s log entries. Processed %s." % (examined_count,processed_count)


### 
### Test Functions
###

def logiter():
    log_grabber = S3LogGrabber(settings('LOG_BUCKET'), settings('LOG_BUCKET_PREFIX'))
    return log_grabber.logiter()
    
def parsedlogiter():
    log_grabber = S3LogGrabber(settings('LOG_BUCKET'), settings("LOG_BUCKET_PREFIX"))
    log_parser = S3LogParser()
    for logline in log_grabber.logiter():
        yield log_parser.parseline(logline)
        
def disp():
    piter = parsedlogiter()
    plog = piter.next()
    count = 0
    while plog:
        if plog['operation'] == 'REST.PUT.OBJECT':
            print plog
            count += 1
        plog = piter.next()
        
        
###
### Process the default log bucket and store in Mongo (this should be run in a cronjob).
###

def main(command):
    log_proc = S3LogProcessor(settings('LOG_BUCKET'), settings('LOG_BUCKET_PREFIX'), db)
    usage_meter = UsageMeter()
    if command == 'nuke':
        print "Resetting log markers, Removing all usage events"
        db.usage_events.remove()
        log_proc.reset_log_marker()
    if command == 'nuke' or command == 'reset':
        print "resetting mapreduce markers"
        usage_meter.reset()
    if command == 'update':
        # Pull updates from S3 logs
        print "Process Amazon logs"
        log_proc.process_new_logs()
        # Update usage stats in DB
        print "Calculate usage from logs"
        usage_meter.update()
        #usage_meter._mr_usage_totals()
        

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

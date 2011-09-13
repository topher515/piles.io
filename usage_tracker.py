from contentstore import S3Store
import pymongo
from db import db
import apachelog
from datetime import datetime
import logging
logger = logging.getLogger()
from utils import FakeLogger
logger = FakeLogger()

from settings import LOG_BUCKET, LOG_BUCKET_PREFIX # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY



class S3LogParser(object):
    def __init__(self):
        self.format = r'%{owner}i %{bucket}i %{datetime}t %{ip}h %{requester}i %{requestid}i %{operation}i %{key}i \"%{requesturi}i\" %{status}s %{error}i %{bytes}b %{objectsize}i %{totaltime}i %{turnaround}i \"%{referer}i\" \"%{useragent}i\" %{versionid}i'
        self.parser = apachelog.parser(self.format)

        self.log_mapper = {
            #'%{owner}i':('owner',None),
            '%{datetime}t':('datetime',lambda dtstr: datetime.strptime(dtstr[:-6].strip('[]'),'%d/%b/%Y:%H:%M:%S ')),
            '%{ip}h':('ip',None),
            '%{requestid}i':('requestid',None),
            '%{operation}i':('operation',None),
            '%{key}i':('key',None),
            '%{requesturi}i':('uri',None),
            '%{requestid}i':('_id',None),
            '%{status}s':('status',None),
            '%{error}i':('error',None),
            '%{bytes}b':('bytes',int),
            '%{versionid}i':('versionid',None),
            '%{objectsize}i':('objectsize',None)
        }


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


class S3LogGrabber(object):
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
    def __init__(self,log_bucket, log_prefix, mongodb): 
        self.bucket = log_bucket
        self.prefix = log_prefix
        self.db = mongodb
        
        self.log_grabber = S3LogGrabber(self.bucket,self.prefix)
        self.log_parser = S3LogParser()

    def _get_last_successful_log(self):
        l = self.db.log_processor.find_one({'_id':'last-successful-log'})
        return l['key'] if l else None
    def _set_last_successful_log(self,key):
        if key:
            logger.debug("Saving position in logs as... %s" % key)
            self.db.log_processor.save({'_id':'last-successful-log','key':key})
    last_successful_log = property(_get_last_successful_log, _set_last_successful_log)


    def process_new_logs(self):
        db = self.db
        
        def extract_pid_fid(plogline):
            s3key = plogline['key']
            index1 = s3key.index('/')
            pid = s3key[:index1]
            remaining = s3key[index1+1:]
            index2 = remaining.index('/')
            fid = remaining[:index2]
            plogline['pid'] = pid
            plogline['fid'] = fid
            return plogline
        
        
        marker_key = self.last_successful_log
        logger.debug("Starting log process at marker: %s " % marker_key)
        plogline = None # We'll want to track this to save for later
        count = 0
        try:
            for logline in self.log_grabber.logiter(marker_key):
                
                count+=1
                
                if not logline:
                    continue # Got a blank for some reason
                
                plogline = self.log_parser.parseline(logline)
            
                if plogline['operation'] == 'REST.GET.OBJECT':
                    try:
                        plogline = extract_pid_fid(plogline)
                    except ValueError:
                        #logger.debug("FAILED TO GET FROM %s" % plogline['key'])
                        continue # Don't bother it's not a customer's get
                    logger.debug("Save get log line %s" % plogline)
                    db.piles.update({'_id':plogline['pid']},{'$inc':{'usage_get':plogline['bytes']}})
                    db.usage_gets.save(plogline)
                    
                
                elif plogline['operation'] == 'REST.PUT.OBJECT':
                    try:
                        plogline = extract_pid_fid(plogline)
                    except ValueError:
                        continue # Don't bother it's not a customer's get
                    logger.debug("Save PUT log line %s" % plogline)
                    db.piles.update({'_id':plogline['pid']},{'$inc':{'usage_put':plogline['objectsize']}})
                    db.usage_puts.save(plogline)
                
                elif plogline['operation'] == 'REST.DELETE.OBJECT': 
                    try:
                        plogline = extract_pid_fid(plogline)
                    except ValueError:
                        continue # Don't bother it's not a customer's get
                    logger.debug("Save DEL log line %s" % plogline)
                    # We should have already recorded usage to the pile when it was deleted through the interface
                    db.usage_dels.save(plogline)
                #else:
                #   db.logs.save(plogline)
        finally:
            self.last_successful_log = self.log_grabber.cur_marker_key
            print "Processed %s log entries..." % count

def logiter():
    log_grabber = S3LogGrabber(LOG_BUCKET, LOG_BUCKET_PREFIX)
    return log_grabber.logiter()
    
def parsedlogiter():
    log_grabber = S3LogGrabber(LOG_BUCKET, LOG_BUCKET_PREFIX)
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
        

def main():
    return S3LogProcessor(LOG_BUCKET, LOG_BUCKET_PREFIX, db).process_new_logs()

if __name__ == '__main__':
    main()

#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
The AppFirst collector API
"""
__all__=['CollectorAPIHandler']

import logging, os
try:
    import ctypes
except Exception as e:
    ctypes = None

if ctypes:
    class CollectorAPIHandler(logging.Handler):

        def __init__(self, *args, **kwargs):
            logging.Handler.__init__(self, *args, **kwargs)
            self.mqueue_name = "/afcollectorapi"
            self.flags = 04001
            self.msgLen = 2048
            self.mqueue = None
            self.shlib = None
            self.pid_override = None
            self.doExcept = False
            self.verbosity = False
            self.typemap = {
                logging.DEBUG: 0,
                logging.INFO: 0,
                logging.WARNING: 1,
                logging.ERROR: 2,
                logging.CRITICAL: 2
            }
       
        def handleError(self, record, emsg = " "):
            if self.mqueue:
                self.close()
                self.mqueue = None
            if self.verbosity:
                print "Error: ", emsg
            if self.doExcept:    
                logging.Handler.handleError(self, record)
        
        def createQueue(self):
            ctypes.cdll.LoadLibrary("librt.so.1")
            self.shlib = ctypes.CDLL("librt.so.1") 
            try:
                self.mqueue = self.shlib.mq_open(self.mqueue_name, self.flags)
                if (self.mqueue < 0) :
                    return False
            except Exception as e:
                return False
            return True
        
        def close(self):
            if self.mqueue:
                try:
                    rc = self.shlib.mq_close(self.mqueue)
                except Exception as e:
                    pass
                self.mqueue = None
            logging.Handler.close(self)
        
        def emit(self, record):
            if not self.mqueue and not self.createQueue():
                self.mqueue = None
                return

            msg = self.format(record)
            severity = self.typemap.get(record.levelno, 0)
            mlen = min(len(msg), self.msgLen)
            mymsg = msg[:mlen]
            # Decode message (which might be a byte-string into unicode object)
            if not isinstance(mymsg, unicode):
                mymsg = msg.decode("utf-8")
            if self.pid_override is None:
                pid = os.getpid()
            else:
                pid = self.pid_override
            post = unicode(pid) + u":" + mymsg
            # convert unicode back to byte stream since we are writing to a low level stream.
            post = post.encode("utf-8")
            if self.verbosity:
                print mlen, post
            try: 
                rc = self.shlib.mq_send(self.mqueue, post, len(post), severity)
                if (rc < 0):
                    self.handleError(record, "mq_send")
            except Exception as e:
                self.handleError(record, "mq_send")
                
else:
    class CollectorAPIHandler(logging.Handler):
        def emit(self, record):
            pass
    
# Test the interface
if __name__ == "__main__":
    capi = CollectorAPIHandler()
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    capi.setFormatter(formatter)
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(capi)
    
    # logging examples
    logger.info(u"This is an !@#$%^&*()<>info msg")
    logger.debug(u"This is a deçg msg")
    logger.warning("This is a warning msg")
    logger.critical("This is a criticæ msg")
    logger.error("This is an error msg") 

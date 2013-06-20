/*
 * Definition of the AppFirst collector API
 */

#ifndef _AFCollectorAPI_H_
#define _AFCollectorAPI_H_

#define AFCollectorAPIName "/afcollectorapi"
#define APICollectorMaxMsgSize 2048
#define APICollectorNumMsg 100

typedef enum AFCollectorMsgSeverity_t {
  AFCSeverityInformation,
  AFCSeverityWarning,
  AFCSeverityCritical,
  AFCSeverityStatsd,
  AFCSeverityPolled
} AFCollectorMsgSeverity;

typedef enum AFCollectorReturnCode_t {
  AFCSuccess,
  AFCNoMemory,
  AFCBadParam,
  AFCOpenError,
  AFCPostError,
  AFCWouldBlock,
  AFCCloseError
} AFCollectorReturnCode;

typedef struct AFCollectorMsg_t {
    AFCollectorMsgSeverity severity;
    int msg_len;
    char *data;
} AFCollectorMsg;


AFCollectorReturnCode postAFCollectorMessage(AFCollectorMsg *msg);

#endif

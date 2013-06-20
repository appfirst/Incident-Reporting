/*
 * Implementation of the collector API
 */
#define _XOPEN_SOURCE 600
#include <sys/types.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <mqueue.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>

#include "AFCollectorAPI.h"
AFCollectorReturnCode
postAFCollectorMessage(AFCollectorMsg *msg)
{
        mqd_t qd;
        pid_t pid;
        size_t len;
        struct timespec abs_timeout;
        AFCollectorReturnCode rc;
        char *post;

        if (!msg || !msg->data || (msg->msg_len > APICollectorMaxMsgSize)) {
            return AFCBadParam;
        }

        qd = mq_open(AFCollectorAPIName, O_WRONLY);
        if (qd < 0) {
            perror("AFCollectorAPI: mq_open");
            return AFCOpenError;
        }

        len = msg->msg_len + (sizeof(pid_t) * 2) + 1;
        post = malloc(len);
        if (!post) {
            perror("AFCollectorAPI : malloc");
            mq_close(qd);
            return AFCNoMemory;
        }

        pid = getpid();

        snprintf(post, len, "%d:%s", pid, msg->data);

        // wait for maximum 5 seconds
        abs_timeout.tv_sec = 5;
        abs_timeout.tv_nsec = 0;
        if (mq_timedsend(qd, post, len, msg->severity, &abs_timeout) < 0) {
            if (errno == EAGAIN) {
                rc = AFCWouldBlock;
            } else {
                rc = AFCPostError;
                perror("AFCollectorAPI : mq_send");
            }
        } else {
            rc = AFCSuccess;
        }

        free(post);
        mq_close(qd);
        return rc;
}

/*
int
main(int argc, char **argv, char* envp[])
{
        int i, num_msgs;
        AFCollectorReturnCode rc;
        AFCollectorMsg msg;
        static char test_data[] = {"This is a test"};

        if (argc < 2) {
            num_msgs = 1;
        } else {
            num_msgs = strtol(argv[1], (char **) NULL, 10);
            if (errno == ERANGE) {
                num_msgs = 1;
                printf("strol out of range for %s defaulting to count of 1\n", argv[2]);
            }
        }

        printf("Client Tests\n");
        msg.severity = AFCSeverityCritical;
        msg.msg_len = sizeof(test_data);
        msg.data = test_data;

        for (i=0; i < num_msgs; i++) {
            printf("%d\n", i);
            rc = postAFCollectorMessage(&msg);
            if (rc == AFCWouldBlock) {
                while (rc == AFCWouldBlock) {
                    sleep(1);
                    rc = postAFCollectorMessage(&msg);
                }
            } else if (rc != AFCSuccess) {
                break;
            }
        }
        printf("done\n");
        return 0;
}
*/

/**
 * 
 */
/**
 * @author AppFirst
 *
 */

import com.sun.jna.Library;
import com.sun.jna.Native;

public class AfCollector {

	private static String AFCollectorAPIName = "/afcollectorapi";
	private static String LibName = "rt";
	private static int O_WRONLY = 01;
	private static int APICollectorMaxMsgSize = 2048;
	 
	public enum AFCollectorMsgSeverity{
	  AFCSeverityInformation,
	  AFCSeverityWarning,
      AFCSeverityCritical,
      AFCSeverityStatsd,
      AFCSeverityPolled;
	
	public static int toInt(AFCollectorMsgSeverity en){
		switch(en){
		case AFCSeverityInformation: { return 0;}
		case AFCSeverityWarning: {return 1;}
		case AFCSeverityCritical: {return 2;}		
		case AFCSeverityStatsd: {return 3;}		
		case AFCSeverityPolled: {return 4;}		
		}
		return -1;
		
	};
	
	}
	
	public enum AFCollectorReturnCode{
	  AFCSuccess,
	  AFCNoMemory,
	  AFCBadParam,
	  AFCOpenError,
	  AFCPostError,
	  AFCWouldBlock,
	  AFCCloseError;
	  
		public static AFCollectorReturnCode fromInt(int i)
		{
			switch(i){
			case 0: {return AFCSuccess;}
			case 1: {return AFCNoMemory;}
			case 2: {return AFCBadParam;}
			case 3: {return AFCOpenError;}
			case 4: {return AFCPostError;}
			case 5: {return AFCWouldBlock;}
			case 6: {return AFCCloseError;}
			}
			return AFCSuccess;
		}
	} 
	
	public interface CLibrary extends Library {
        CLibrary INSTANCE = (CLibrary)
            Native.loadLibrary("c", CLibrary.class);
    
        int getpid();
    }
	
	public interface MQ extends Library {
        public int mq_open(String filename, int mode);
        public int mq_close(int mqd);
        public int mq_send(int mqd, String msg, int len, int prio);
   }
	
	
	static AFCollectorReturnCode postAFCollectorMessage(AFCollectorMsgSeverity severity, String msg)
	{
		int len = msg.length();
		if (len > APICollectorMaxMsgSize) {
			return AFCollectorReturnCode.AFCBadParam;
		}
		
		int pid = CLibrary.INSTANCE.getpid();
		int prio = AFCollectorMsgSeverity.toInt(severity);
		int rv = 0;
		
		MQ mq = (MQ) Native.loadLibrary(LibName, MQ.class);
		
		int mqd = mq.mq_open(AFCollectorAPIName, O_WRONLY);
		
		String incident = pid + ":" + msg;
		len = incident.length();
		
		rv = mq.mq_send(mqd, incident, len, prio);
		
		mq.mq_close(mqd);
		
		return AFCollectorReturnCode.fromInt(rv);
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		
        int i, num_msgs;
        AFCollectorReturnCode rc;
        
        String test_data = "This is a test:";

        if (args.length < 1) {
            num_msgs = 1;
        } else {
        	try
        	{
        		num_msgs = Integer.parseInt(args[0]);
        	}
        	catch(NumberFormatException e)
            {
                num_msgs = 1;
                System.out.printf("could not determine number of cycles by %s defaulting to count of 1", args[0]);
            }
        }

        System.out.print("Client Tests\n");
               
        for (i=0; i < num_msgs; i++) {
        	
        /*	
	System.out.printf("%d\n", i);
         */
        	rc = AfCollector.postAFCollectorMessage(AFCollectorMsgSeverity.AFCSeverityCritical,test_data);
                System.out.printf("Count=%d rc=%s\n",i,rc);

		try{
                    Thread.sleep(1000);
                }catch(InterruptedException e){
                        e.printStackTrace();
                }
            
            if (rc == AFCollectorReturnCode.AFCWouldBlock) {
                while (rc == AFCollectorReturnCode.AFCWouldBlock) {
		try{
                    Thread.sleep(1000);
		}catch(InterruptedException e){
			e.printStackTrace();
		}
                    rc = AfCollector.postAFCollectorMessage(AFCollectorMsgSeverity.AFCSeverityCritical,test_data);
                }
            } else if (rc != AFCollectorReturnCode.AFCSuccess) {
                break;
            }
        }

        System.out.print("done\n");   
	}
}

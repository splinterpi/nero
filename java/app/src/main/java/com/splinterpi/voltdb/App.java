package com.splinterpi.voltdb;

import java.io.IOException;
import java.net.UnknownHostException;

import org.voltdb.VoltTable;
import org.voltdb.client.Client;
import org.voltdb.client.ClientFactory;
import org.voltdb.client.ClientResponse;
import org.voltdb.client.NoConnectionsException;
import org.voltdb.client.ProcCallException;

/**
 * Hello world!
 *
 */
public class App {
	public static void main( String[] args )
    {
        
		Client client = ClientFactory.createClient();
		try {
			client.createConnection("localhost");
		} catch (UnknownHostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        
        long starttime = System.currentTimeMillis();
        long timelimit = 5 * 60 * 1000; // 5 mins
        long currenttime = starttime;
		
		while(currenttime - starttime < timelimit) {
        	
        
		
		try {
			ClientResponse response = client.callProcedure("BANK_ACCOUNT.select", 1234);
			
			if (response.getStatus() != ClientResponse.SUCCESS){
				
				System.out.println();
			} else{
				
				VoltTable[] results = response.getResults();
			    int balance = (int) results[0].fetchRow(0).getLong("BALANCE");
			    System.out.println("Balance: " + balance);
			    
			    currenttime = System.currentTimeMillis();
			}
		} catch (NoConnectionsException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ProcCallException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        }
    }
}

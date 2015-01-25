package com.splinterpi.voltdb;

import java.io.IOException;
import java.net.UnknownHostException;
import java.util.Random;

import org.voltdb.VoltTable;
import org.voltdb.VoltTableRow;
import org.voltdb.client.Client;
import org.voltdb.client.ClientFactory;
import org.voltdb.client.ClientResponse;
import org.voltdb.client.NoConnectionsException;
import org.voltdb.client.ProcedureCallback;

/**
 * Hello world!
 *
 */
public class App {
	public static void main(String[] args) {

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

		while (currenttime - starttime < timelimit) {

			Random rand = new Random(System.currentTimeMillis());
			int accountId = rand.nextInt(200 - 1) + 1;

			try {

				ProcedureCallback callback = new ProcedureCallback() {
					public void clientCallback(ClientResponse response)
							throws InterruptedException {
						if (response.getStatus() != ClientResponse.SUCCESS) {
							System.out.println("Error: voltdb call error");
						} else {
							VoltTable[] results = response.getResults();
							VoltTableRow row = results[0].fetchRow(0);
							int balance = (int) row.getLong("BALANCE");
							int accountId = (int) row.getLong("ACCOUNT_ID");
							System.out.println("Account: " + accountId + " Balance: " + balance);

						}
					}
				};
				client.callProcedure(callback, "BANK_ACCOUNT.select", accountId);

				currenttime = System.currentTimeMillis();

			} catch (NoConnectionsException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
}

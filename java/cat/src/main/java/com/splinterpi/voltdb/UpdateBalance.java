package com.splinterpi.voltdb;

import org.voltdb.ProcInfo;
import org.voltdb.SQLStmt;
import org.voltdb.VoltProcedure;
import org.voltdb.VoltTable;

@ProcInfo (
	    partitionInfo = "BANK_ACCOUNT.ACCOUNT_ID:0",
	    singlePartition = true
	)

public class UpdateBalance extends VoltProcedure { 
	
	public final SQLStmt updateSQL = new SQLStmt(        
		        "UPDATE BANK_ACCOUNT SET BALANCE = ?" +
		        " WHERE ACCOUNT_ID = ?;");
		 
		    public VoltTable[] run(int account_id, int balance) 
		        throws VoltAbortException {  
		    	
		        voltQueueSQL( updateSQL
		        		     ,balance
		        		     ,account_id);             
		        return voltExecuteSQL();                   
		}
}


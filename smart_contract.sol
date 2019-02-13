pragma solidity ^0.5.3;

contract UPI
{
	//BankAccount: Custom datatype to represent a bank account
	struct BankAccount
	{
		uint balance;
		bytes32 holder_name;
		uint pin;
	}

	

	//One more type to record transactions?
	
	//mapping(address => BankAccount) public accounts; will create a bank account
	//for evey address
	mapping(uint => BankAccount) public g_bank_accounts; 
	mapping(bytes32 => uint) public g_upi_addrs;//All locations value is zero

	constructor(uint[] memory balances, bytes32[] memory holder_names, bytes32[] memory upi_addrs, uint[] memory pins, uint[] memory account_numbers) public
	{
		for(uint i = 0;i < balances.length; i++)
		{
			g_upi_addrs[upi_addrs[i]] = account_numbers[i];

			BankAccount memory bank_account = BankAccount(
				balances[i],
				holder_names[i],
				pins[i]
			);
			g_bank_accounts[account_numbers[i]] = bank_account;
		}
	}

	function verifyUPIAddr(bytes32 upi_addr) public view returns (bytes32)
	{
		bytes32 holder_name = "NA";

		if (g_upi_addrs[upi_addr] == 0)
		{
			return holder_name;
		}
		else
		{
			holder_name = g_bank_accounts[g_upi_addrs[upi_addr]].holder_name;
		}

		return holder_name;
	}

	function sendMoney(bytes32 from_upi_addr, bytes32 to_upi_addr, uint pin, uint amount) public
	{
		if(g_upi_addrs[from_upi_addr] == 0 || g_upi_addrs[to_upi_addr] == 0)
		{
			return;
		}

		if(g_bank_accounts[g_upi_addrs[from_upi_addr]].balance < amount || g_bank_accounts[g_upi_addrs[from_upi_addr]].pin != pin)
		{
			return;
		}
		
		BankAccount storage bank_account_from = g_bank_accounts[g_upi_addrs[from_upi_addr]];
		bank_account_from.balance -= amount;

		BankAccount storage bank_account_to = g_bank_accounts[g_upi_addrs[to_upi_addr]];
		bank_account_to.balance += amount;

	}

	function getBalance(uint account_number, uint pin) public view returns (int)
	{
		if(g_bank_accounts[account_number].holder_name.length == 0)
		{
			return -1;
		}
		if(g_bank_accounts[account_number].pin != pin)
		{
			return -1;
		}

		return int(g_bank_accounts[account_number].balance);
	}

	function getBalanceUPI(bytes32 upi_addr, uint pin) public view returns (int)
	{
		if(g_upi_addrs[upi_addr] == 0)
		{
			return -1;
		}
		if(g_bank_accounts[g_upi_addrs[upi_addr]].pin != pin)
		{
			return -1;
		}
		
		return int(g_bank_accounts[g_upi_addrs[upi_addr]].balance);
	}
}

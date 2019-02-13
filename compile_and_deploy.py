import subprocess
import json
from web3 import Web3,HTTPProvider
from web3.contract import Contract
import sys
import array
from eth_abi import encode_single, decode_single

def compile(file_name, contract_name):
    result = subprocess.run(['solc','--combined-json','abi,bin',file_name], stdout=subprocess.PIPE)
    compiled = result.stdout.decode('utf-8')
    compiled = json.loads(compiled)
    abi = compiled['contracts'][file_name + ':' + contract_name]['abi']
    binary = compiled['contracts'][file_name + ':' + contract_name]['bin']
    return abi,binary

def writeToFile(contract_address):
    f = open("con_addr","w")
    f.write(contract_address)
    f.close()

def readFromFile():
    f = open("con_addr")
    return f.read()

isdeploy_contract = int(sys.argv[1])
file_name = "smart_contract.sol"
contract_name = "UPI"
ip = "127.0.0.1"
port = "30304"
eth_password = "pass1234"

abi,binary = compile(file_name, contract_name)

web3 = Web3(HTTPProvider("http://" + ip + ":" + port))
web3.personal.unlockAccount(web3.eth.accounts[0],"pass1234", 3600)
web3.eth.defaultAccount = web3.eth.accounts[0] #Do this, or send from param in every eth call

#Just an object of the contract
UPI = web3.eth.contract(abi = abi, bytecode = binary)

#Deploy the contract
balances = [10000,10000]
balances_en = encode_single('uint[]',balances)

names = ['Satoshi Nakamoto','Vitalik Buterin']
names = [n.encode('utf-8') for n in names]
names_en = encode_single('bytes32[]',names)

pins = [1234, 5678]
pins_en = encode_single('uint[]',pins)

upi_addrs = ['sn@bitcoin','vb@eth']
upi_addrs = [u.encode('utf-8') for u in upi_addrs]
upi_addrs_en = encode_single('bytes32[]',upi_addrs)

acc_nos = [1,2]
acc_nos_en = encode_single('uint[]',acc_nos)

print("\nOur Bank DB: ")
for i in range(2):
    print("Holder name: %s"%names[i].decode('utf-8'))
    print("Acc no: %s"%acc_nos[i])
    print("Pin no: %s"%pins[i])
    print("UPI Addr: %s"%upi_addrs[i].decode('utf-8'))
    print("-------------------------------\n\n")

if isdeploy_contract == 1:
    web3.miner.start(1)
    tx_hash = UPI.constructor(balances, names, upi_addrs, pins, acc_nos).transact()
    #Wait for txn to be added to the blockchain
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    web3.miner.stop()

    contract_address = tx_receipt.contractAddress
    writeToFile(contract_address)

else: 
    contract_address = readFromFile()

#Create an instance of the deployed contract
upi = web3.eth.contract(address = contract_address, abi= abi)

def verifyUPIAddr(upi_addr):
    global upi
    upi_addr = str(upi_addr).encode('utf-8')
    ret_value = upi.functions.verifyUPIAddr(upi_addr).call()

    return decode_single('bytes32',ret_value).decode('utf-8')

def sendMoney(from_upi_addr, to_upi_addr, pin, amount):
    global upi,web3
    from_upi_addr = str(from_upi_addr).encode('utf-8')
    to_upi_addr = str(to_upi_addr).encode('utf-8')

    web3.miner.start(1)
    tx_hash =  upi.functions.sendMoney(from_upi_addr, to_upi_addr, pin, amount).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    web3.miner.stop()

def getBalance(acc_no, pin):
    global upi
    return upi.functions.getBalance(acc_no,pin).call()

def getBalanceUPI(upi_addr, pin):
    global upi
    upi_addr = str(upi_addr).encode('utf-8')
    pin = int(pin)

    return upi.functions.getBalanceUPI(upi_addr, pin).call()


while True:
    print("\n\n------------------------------------")
    print("1. Print balance")
    print("2. Verify UPI address")
    print("3. Send money")
    print("4. Exit")
    choice = int(input("Enter choice: "))
   
    if choice > 3 or choice < 1:
        break

    upi_addr = str(input("Your UPI addr: "))
    pin = int(input("Pin: "))


    if choice == 1:
        print("Balance: %s"%getBalanceUPI(upi_addr, pin))

    elif choice == 2:
        print("Verify UPI addr: %s, Verified Holder name: %s"%(upi_addr, verifyUPIAddr(upi_addr)))

    elif choice == 3:
        to_upi_addr = str(input("Reciever's UPI addr: "))
        amount = int(input("Amount: "))
        sendMoney(upi_addr, to_upi_addr, pin, amount)
        print("Transaction carried out, not sure if successful or not.")
        print("Sender Balance: %s"%getBalanceUPI(upi_addr, pin))


web3.miner.stop()


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

names = ['a b','b c']
names = [n.encode('utf-8') for n in names]
names_en = encode_single('bytes32[]',names)

pins = [1234, 5678]
pins_en = encode_single('uint[]',pins)

upi_addrs = ['a.b@bank','b.c@bank']
upi_addrs = [u.encode('utf-8') for u in upi_addrs]
upi_addrs_en = encode_single('bytes32[]',upi_addrs)

acc_nos = [0,1]
acc_nos_en = encode_single('uint[]',acc_nos)

web3.miner.start(1)

if isdeploy_contract == 1: 
    tx_hash = UPI.constructor(balances, names, upi_addrs, pins, acc_nos).transact()
    #Wait for txn to be added to the blockchain
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    
    contract_address = tx_receipt.contractAddress
    writeToFile(contract_address)
    
contract_address = readFromFile()
#Create an instance of the deployed contract
upi = web3.eth.contract(address = contract_address, abi= abi)

#One UPI txn
ret_value = upi.functions.verifyUPIAddr(upi_addrs[1]).call()
print("verify: %s"%decode_single('bytes32',ret_value).decode('utf-8'))

tx_hash = ret_value = upi.functions.sendMoney(acc_nos[0], upi_addrs[1], pins[0], 1000).transact()

web3.eth.waitForTransactionReceipt(tx_hash)
print("send money: %s"%ret_value)

ret_value = upi.functions.getBalance(acc_nos[0],pins[0]).call()
print("first get bal: %s"%ret_value)

ret_value = upi.functions.getBalance(acc_nos[1],pins[1]).call()
print("second get bal: %s"%ret_value)

web3.miner.stop()


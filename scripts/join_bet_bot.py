#!/usr/bin/python3
import json
from web3 import Web3
from brownie import accounts, config, interface, network
from brownie.convert import to_address

infura_kovan = config["networks"]["kovan"]["web3_id"]
infura_link = 'https://kovan.infura.io/v3/' + infura_kovan
print(f'{infura_kovan = }')
print(f'{infura_link = }')
web3 = Web3(Web3.HTTPProvider(infura_link))

contractBettingEvent = {'bettingPairId': 0, 'priceFeed': 1, 'priceFeedAddress' : 2, 'priceFeedName' : 3, 'currentPriceFromChainLink': 4, 'player1' : 5 , 'player2' : 6, 'player1Deposit' : 7, 'player2Deposit' : 8, 'player1PricePrediction' : 9 , 'player2PricePrediction' : 10, 'gameFinished' : 11, 'withdrawCompleted' : 12, 'theWinner' : 13, 'gains' : 14}

def read_all_bets(contract):
    betcount = contract.functions.betCount().call()
    print(betcount)

    allBets = contract.functions.getActiveBets().call()
    for bet in allBets:
        #print(bet)
        print ("-----")
        for item in bet:
            print(item)

def read_join_bet_parameters():
    f = open('bet_parameters.json',)
    data = json.load(f)
    print(data)

    price_feed = data['price_feed']
    bet_amount = data['bet_amount']
    price_prediction = int(data['price_prediction'])
    f.close()
    return price_feed, bet_amount, price_prediction

def find_interesting_bets(contract, account, from_key):
    allBets = contract.functions.getActiveBets().call()
    for bet in allBets:
        #print(bet)
        print ("-----")
        for item in bet:
            print(item)
        #print ("-----")
        #print(bet[contractBettingEvent['theWinner']])
        #print(not bet[contractBettingEvent['withdrawCompleted']])

        bet_id = bet[contractBettingEvent['bettingPairId']]
        if (bet[contractBettingEvent['player2']] == '0x0000000000000000000000000000000000000000'):
            print('found vacant bet : ' + str(bet_id))
            if (bet[contractBettingEvent['player1']] != account):
                print('definetly join this bet')
                [pricefeed, bet_amount, price_prediction] = read_join_bet_parameters()
                join_bet(contract, account, from_key, bet_id, bet_amount, price_prediction)
            else:
                print('you created this bet, so don\'t join')
        elif (bet[contractBettingEvent['theWinner']] == account and not bet[contractBettingEvent['withdrawCompleted']]):
            withdraw(contract, account, from_key, bet_id)

def join_bet(contract, account, from_key, bet_id, bet_amount, price_prediction):

    print('joining bet with bet_id = ' + str(bet_id) + ' bet_amount = ' + bet_amount + ' price_prediction =' + str(price_prediction))

    tx = contract.functions.joinBet(bet_id, price_prediction).buildTransaction({'nonce': web3.eth.getTransactionCount(to_address(account)), "from": to_address(account), "value": web3.toWei(bet_amount,'ether')})

    signed_tx = web3.eth.account.signTransaction(tx, private_key=from_key)
    print(f'{signed_tx = }')

    raw_tx = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'{raw_tx = }')

def withdraw(contract, account, from_key, bet_id):

    print('Withdraw winnings from ' + str(bet_id))
    tx = contract.functions.withdraw(bet_id).buildTransaction({'nonce': web3.eth.getTransactionCount(to_address(account)), "from": to_address(account)})

    signed_tx = web3.eth.account.signTransaction(tx, private_key=from_key)
    print(f'{signed_tx = }')

    raw_tx = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'{raw_tx = }')

def main():

    f = open('contract_abi/MultiBetContract.json',)
    data = json.load(f)

    abi = data['abi']
    contract_address = config["networks"]["kovan"]["contract_address"]
    print(f'{contract_address = }')

    contract = web3.eth.contract(address=contract_address, abi=abi)
    print(contract.address)
    private_key = config["wallets"]["from_key"]
    account = accounts.add(config["wallets"]["from_key"])
    print(f'{account = }')

    #read_all_bets(contract)

    find_interesting_bets(contract, account, private_key)
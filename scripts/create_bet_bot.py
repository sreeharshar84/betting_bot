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

kovanTokenConversions = {"LINK / USD" : "0x396c5E36DD0a0F5a5D33dae44368D4193f69a1F0", "ETH / USD" : "0x9326BFA02ADD2366b30bacB125260Af641031331", "AAVE / ETH" : "0xd04647B7CB523bb9f26730E9B6dE1174db7591Ad", "AMPL / ETH" : "0x562C092bEb3a6DF77aDf0BB604F52c018E4f2814", "AUD / USD" : "0x5813A90f826e16dB392abd2aF7966313fc1fd5B8", "BAT / ETH" : "0x0e4fcEC26c9f85c3D714370c98f43C4E02Fc35Ae"}

def read_all_bets(contract):
    betcount = contract.functions.betCount().call()
    print(betcount)

    allBets = contract.functions.getActiveBets().call()
    for bet in allBets:
        #print(bet)
        print ("-----")
        for item in bet:
            print(item)

def read_bet_parameters():
    f = open('bet_parameters.json',)
    data = json.load(f)
    print(data)

    price_feed = data['price_feed']
    bet_amount = data['bet_amount']
    price_prediction = int(data['price_prediction'])
    f.close()
    return price_feed, bet_amount, price_prediction

def create_bet(contract, account, from_key):
    [pricefeed, bet_amount, price_prediction] = read_bet_parameters()
    print('Creating bet on = ' + pricefeed + ' bet_amount = ' + bet_amount + ' price_prediction =' + str(price_prediction))
    kovanTokenConversionAddress = kovanTokenConversions[pricefeed]
    print(f'{kovanTokenConversionAddress = }')

    tx = contract.functions.createBet(pricefeed, kovanTokenConversionAddress, price_prediction).buildTransaction({'nonce': web3.eth.getTransactionCount(to_address(account)), "from": to_address(account), "value": web3.toWei(bet_amount,'ether')})

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

    create_bet(contract, account, private_key)
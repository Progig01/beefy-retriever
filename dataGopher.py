# Import Libraries
from bs4 import BeautifulSoup
import requests
import json


#  Scrape TheTopDefi for holdings total and net yield
def getTopDefi(address):
    # Get the page and create a Beautiful soup object of it
    URL = "https://thetopdefi.com/dashboard/views?v=2&chain=all&walletAddress=" + address
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # Isolate the pages script and load it into a dictionary called data
    script = soup.find('script', id="__NEXT_DATA__")
    data = json.loads(script.string)
    # Make accessing data a little easier
    data = data['props']['pageProps']['data']

    return data  # Yeet


#   Connect to the Beefy Finance API for vault rates, tvls, etc
def getBeefy(vault):
    URL = "http://api.beefy.finance/apy/breakdown"
    page = requests.get(URL)

    data = json.loads(page.text)
    return data[vault]


#   Take a snapshot of our current investment state
def takeSnapshot(address):
    # Get info on current investments from TheTopDefi
    snapshot = getTopDefi(address)
    for chain in snapshot:  # For every blockchain we're invested in...
        # Make an empty list to store vaults in!
        chain.update({'vaults': []})
        # For every vault in the current chain...
        for vault in chain['gridView']:
            # Get the name of the vault we're iterating over...
            vName = vault['vid']
            # And append it to the vaults list along with its name!
            chain['vaults'].append({vName: getBeefy(vName)})
    return snapshot


#   Make a function for creating an easily readable view of a given vault
def getVaultInfo(snapshot, chain, vault):
    topDefi = {}
    beefyFi = {}

    chains = 0
    while chains < len(snapshot):
        vaults = 0
        while vaults < len(snapshot[chains]) - 6:
            if vault in snapshot[chains]['gridView'][vaults]['vid']:
                beefyFi = snapshot[chains]['vaults'][vaults][vault]
                topDefi = snapshot[chains]['gridView'][vaults]
            vaults += 1
        chains += 1

    # Make a dictionary to store cleaned data in
    rVault = {}

    # Store useful data from Beefy Finance
    #   General Info
    rVault.update({"vault_apy%": beefyFi['totalApy'] * 100})
    rVault.update({"vault_apr$": beefyFi['vaultApr'] * 100})
    rVault.update({"vault_yearlyCompoundings": beefyFi['compoundingsPerYear']})
    rVault.update({"vault_performanceFee": beefyFi['beefyPerformanceFee']})
    rVault.update({"vault_lpFee": beefyFi['lpFee']})

    # Store useful data from TopDefi
    #   General Info
    rVault.update({"vault_chain": chain})
    rVault.update({"vault_name":  topDefi['vid']})
    rVault.update({"vault_holdings$": topDefi['cr_LP_usd']})
    rVault.update({"vault_holdings$": topDefi['cr_LP_usd']})
    rVault.update({"vault_net$": topDefi['yi_net_usd']})
    rVault.update({"vault_net%": topDefi['yi_net_pct']})
    rVault.update({"vault_gross$": topDefi['yi_gross_usd']})
    rVault.update({"vault_gross%": topDefi['yi_gross_pct']})
    rVault.update({"vault_il$": topDefi['il_usd']})
    rVault.update({"vault_il%": topDefi['il_pct']})
    #   LP Token A Info
    rVault.update({"token_a_name": topDefi['Tokens'][0]['n']})
    rVault.update({"token_a_symbol": topDefi['Tokens'][0]['s']})
    rVault.update({"token_a_holdingT": topDefi['Tokens'][0]['cb_amt']})
    rVault.update({"token_a_price": topDefi['Tokens'][0]['cb_usd']})
    rVault.update(
        {"token_a_holding$": topDefi['Tokens'][1]['cb_usd'] * topDefi['Tokens'][0]['cb_amt']})
    #   LP Token B Info
    rVault.update({"token_b_name": topDefi['Tokens'][1]['n']})
    rVault.update({"token_b_symbol": topDefi['Tokens'][1]['s']})
    rVault.update({"token_b_holdingT": topDefi['Tokens'][1]['cb_amt']})
    rVault.update({"token_b_price": topDefi['Tokens'][1]['cb_usd']})
    rVault.update(
        {"token_a_holding$": topDefi['Tokens'][1]['cb_usd'] * topDefi['Tokens'][0]['cb_amt']})

    # Yeet
    return rVault


#   Make a function for getting the names of all vaults on a chain
def getVaults(snapshot, chain):
    vaults = []

    for chain in snapshot:
        for vault in chain['gridView']:
            vaults.append(vault['vid'])

    return vaults


#   Make a function for getting the names of all chains on a snapshot
def getChains(snapshot):
    chains = []
    for chain in snapshot:
        chains.append(chain['chain'])
    return chains


#   Build a structured portfolio from only a wallet address
def buildPortfolio(address):
    snapshot = takeSnapshot(address)
    portfolio = {}

    # Make an empty dictionary to organize chains into
    portfolio.update({"chains": {}})
    # Make an empty nested dictionary for each chain bearing its name
    for chain in getChains(snapshot):
        portfolio['chains'].update({chain: {}})  # Doing that ^
        # Make an empty nested dict to organize vaults into
        portfolio['chains'][chain].update({"vaults": {}})
        # Get all the vault names for the chain provided
        for vault in getVaults(snapshot, chain):
            # Make an empty nested dict for each vault bearing its name and populate it with data
            portfolio['chains'][chain]['vaults'].update(
                {vault: getVaultInfo(snapshot, chain, vault)})

    return portfolio

from dotenv import load_dotenv
from eth_account import Account
from vyper import compile_code
from web3 import Web3

import getpass
import os

from encrypt_key import KEYSTORE_PATH

load_dotenv()

RPC_URL = os.getenv("RPC_URL")

# ! NB: Make sure this matches your virtual or anvil network
CHAIN_ID = 31337

def decrypt_key() -> str:
    with KEYSTORE_PATH.open("r") as fp:
        encrypted_account = fp.read()

        password = getpass.getpass("Enter your password:\n")

        key = Account.decrypt(encrypted_account, password)

        print("Decrypted key successfully!")

        return key

def main():
    print("Let's read in the Vyper code and deploy it!")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()

        compliation_details = compile_code(favorites_code, output_formats=["bytecode", "abi"])

        print("Getting environment variables...")
        MY_ADDRESS = os.getenv("MY_ADDRESS")
        PRIVATE_KEY = decrypt_key()

        favorites_contract = w3.eth.contract(bytecode=compliation_details["bytecode"], abi=compliation_details["abi"])

        print("Building the transaction...")
        nonce = w3.eth.get_transaction_count(MY_ADDRESS)

        transaction = favorites_contract.constructor().build_transaction({
            "chainId": CHAIN_ID,
            "from": MY_ADDRESS,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
        })

        print("Signing the transaction...")
        signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)

        print("Deploying the contract...")
        tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)

        print("Waiting for the transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Done! The contract was deployed to {tx_receipt.contractAddress}")



if __name__ == "__main__":
    main()
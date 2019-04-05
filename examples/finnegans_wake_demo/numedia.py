import datetime
import os
import shutil
import sys
import json
import struct
import time
from time import sleep

import maya
from twisted.logger import globalLogPublisher

from umbral.keys import UmbralPublicKey
from nucypher.characters.lawful import Alice, Bob, Ursula
from nucypher.characters.lawful import Enrico as Enrico
from nucypher.crypto.powers import SigningPower
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import SimpleObserver

from flask import Flask
from flask import request, render_template, redirect, url_for
UPLOAD_FOLDER = './static/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import re
import json
import ipfsapi

# Execute the download script (download_finnegans_wake.sh) to retrieve the book
BOOK_PATH = os.path.join('.', '1st_chapter.txt')

# Twisted Logger
globalLogPublisher.addObserver(simpleObserver)

# Temporary file storage
TEMP_FILES_DIR = "{}/examples-runtime-cruft".format(os.path.dirname(os.path.abspath(__file__)))
TEMP_DEMO_DIR = "{}/finnegans-wake-demo".format(TEMP_FILES_DIR)
TEMP_CERTIFICATE_DIR = "{}/certs".format(TEMP_DEMO_DIR)

# Remove previous demo files and create new ones
shutil.rmtree(TEMP_FILES_DIR, ignore_errors=True)
os.mkdir(TEMP_FILES_DIR)
os.mkdir(TEMP_DEMO_DIR)
os.mkdir(TEMP_CERTIFICATE_DIR)

#######################################
# Finnegan's Wake on NuCypher Testnet #
# (will fail with bad connection) #####
#######################################

TESTNET_LOAD_BALANCER = "eu-federated-balancer-40be4480ec380cd7.elb.eu-central-1.amazonaws.com"

##############################################
# Ursula, the Untrusted Re-Encryption Proxy  #
##############################################
ursula = Ursula.from_seed_and_stake_info(host=TESTNET_LOAD_BALANCER,
                                         certificates_directory=TEMP_CERTIFICATE_DIR,
                                         federated_only=True,
                                         minimum_stake=0)


@app.route("/")
def startpage():
    return render_template('allprojects.html')
    
@app.route("/allprojects")
def allprojects():
    return render_template('allprojects.html')    
    
@app.route("/myprojects")
def myprojects():
    return render_template('myprojects.html')
    
@app.route("/subs")
def subs():
    return render_template('subs.html')
    
@app.route("/demodata")
def get_data():
	policy_end_datetime = maya.now() + datetime.timedelta(days=5)
    m, n = 2, 3  
    label = b"secret/files/and/stuff"

    ######################################
    # Alice, the Authority of the Policy # 
    ######################################
    ALICE = Alice(network_middleware=RestMiddleware(),
                  known_nodes=[ursula],
                  learn_on_same_thread=True,
                  federated_only=True,
                  known_certificates_dir=TEMP_CERTIFICATE_DIR)      
    BOB = Bob(known_nodes=[ursula],
              network_middleware=RestMiddleware(),
              federated_only=True,
              start_learning_now=True,
              learn_on_same_thread=True,
              known_certificates_dir=TEMP_CERTIFICATE_DIR)
    ALICE.start_learning_loop(now=True)
    policy = ALICE.grant(BOB,
                         label,
                         m=m, n=n,
                         expiration=policy_end_datetime)

    # Alice puts her public key somewhere for Bob to find later...
    alices_pubkey_bytes_saved_for_posterity = bytes(ALICE.stamp)

    # ...and then disappears from the internet.    
    del ALICE

    BOB.join_policy(label, alices_pubkey_bytes_saved_for_posterity)

    # Now that Bob has joined the Policy, let's show how Enrico the Encryptor
    # can share data with the members of this Policy and then how Bob retrieves it.
    with open(BOOK_PATH, 'rb') as file:
        finnegans_wake = file.readlines()
  
    for counter, plaintext in enumerate(finnegans_wake):

        #########################
        # Enrico, the Encryptor #
        #########################
        enciro = Enrico(policy_pubkey_enc=policy.public_key)

        # In this case, the plaintext is a
        # single passage from James Joyce's Finnegan's Wake.
        # The matter of whether encryption makes the passage more or less readable
        # is left to the reader to determine.
        single_passage_ciphertext, _signature = enciro.encapsulate_single_message(plaintext)
        data_source_public_key = bytes(enciro.stamp)
        del enciro

        ###############
        # Back to Bob #
        ###############

        enrico_as_understood_by_bob = Enrico.from_public_keys(
            policy_public_key=policy.public_key,
            datasource_public_key=data_source_public_key,
            label=label
        )

        # Now Bob can retrieve the original message.
        alice_pubkey_restored_from_ancient_scroll = UmbralPublicKey.from_bytes(alices_pubkey_bytes_saved_for_posterity)
        delivered_cleartexts = BOB.retrieve(message_kit=single_passage_ciphertext,
                                        data_source=enrico_as_understood_by_bob,
                                        alice_verifying_key=alice_pubkey_restored_from_ancient_scroll)

        # We show that indeed this is the passage originally encrypted by Enrico.
        assert plaintext == delivered_cleartexts[0]
        #print("Retrieved: {}".format(delivered_cleartexts[0]))
    return render_template('demodata.html')

if __name__ == '__main__':
    app.run(debug=True, host="livedemo.su")

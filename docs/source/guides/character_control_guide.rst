================================
NuCypher Character Control Guide
================================

The `Character Control` is a module that contains useful REST-like HTTP endpoints for working with NuCypher characters.

.. important::

   Character control is currently a Work-In-Progress. Expect large, and even breaking, changes to this API often.

.. warning::

    Character control is currently not intended for use over remote connections or on shared machines.
    The current API has not been secured and should not be used for production applications.

.. contents:: Table of Contents
   :depth: 4


API Request/Response Structure Overview
=======================================

Status Codes
------------
All documented API endpoints use JSON and are REST-like.

Some common returned status codes you may encounter are:

- ``200 OK`` -- The request has succeeded.
- ``400 BAD REQUEST`` -- The server cannot or will not process the request due to something that is perceived to be a client error (e.g., malformed request syntax, invalid request message framing, or deceptive request routing).
- ``500 INTERNAL SERVER ERROR`` -- The server encountered an unexpected condition that prevented it from fulfilling the request.

Typically, you will want to ensure that any given response from a character control endpoint results in a 200 status code.
This tells you that the server successfully completed the call.

If you are returned a 400, check the data that you're sending to the server.
See below for what the character control API expects.

.. _`Contribution Guide`: https://docs.nucypher.com/en/latest/guides/contribution_guide.html/
.. _`Discord`: https://discord.gg/7rmXa3S

If you are ever given a 500 status code, we'd like to know about it!
You can see our `Contribution Guide`_ for getting involved.
Ideally, you can share some information with us about what you were doing when you encountered the 500 in the form of a GitHub issue, or just tell us in our `Discord`_.

HTTP Methods
------------
Currently, the character control API only uses the following HTTP methods:

- ``POST``
- ``PUT``

We don't exactly follow RESTful methodology precisely.
Take careful note following the API endpoints to see what to send and what to expect as a response.

Request Format
--------------
The character control API uses JSON for all its endpoints. A request may look like:

.. code::

    {
        'bob_encrypting_key': '0324df67664e6ea40f2eea8037c994debd4caa42117fe86cdb8cab6ac7728751ad',
        'label': 'dGVzdA==',
        'm': 2,
        'n': 3,
        'expiration_time': '2019-02-14T22:23:10.771093Z',
    }

Take a look at ``bob_encrypting_key``. Take note that it's a hex-encoded string.
The character control API endpoints expect `all` keys to be encoded as hex.

Now, look at ``label``. Notice that it's a base64-encoded string.
Whenever the Python API expects the ``bytes`` type, the character control API will expect a base64 encoded string.

Integers, in our case ``m`` and ``n`` can be passed as is without encoding.

A datetime, like ``expiration_time``, must be passed in as an ISO-8601 formatted datetime string.

If you are missing a required argument in your request, you will be returned a 400 status code.

Response Format
---------------
Like we determined above, the character control API uses JSON for all its endpoints.
The same goes for our API's responses. One may look like:

.. code::

    {
        'result': {
            'treasure_map': 'Y8Wl+o...Jr4='
        }
    }

The character control API will return the results of our Python API.
If any data is returned, like a treasure map or a message kit, it will be serialized as base64 with the object name being a key inside ``result``.

Be sure to also check the returned status code of the request. All successful calls will be 200.
See the above "Status Codes" section on what to do in the event of a 400 or 500.

Character Control Endpoints
===========================

Alice
-----

derive_policy_pubkey
~~~~~~~~~~~~~~~~~~~~

This endpoint controls the ``Alice.get_policy_pubkey_from_label`` method.

- URL: ``/derive_policy_pubkey``
- HTTP Method: ``PUT``
- Required arguments:
   - ``label`` -- encoded as base64
- Returns: a hex-encoded ``policy_encrypting_pubkey``

grant
~~~~~

This endpoint controls the ``Alice.grant`` method.

- URL: ``/grant``
- HTTP Method: ``PUT``
- Required arguments:
    - ``bob_encrypting_key`` -- encoded as hex
    - ``label`` -- encoded as base64
    - ``m`` -- an integer
    - ``n`` -- an integer
    - ``expiration_time`` -- an ISO-8601 formatted datetime string
- Returns:
    - ``treasure_map`` -- encoded as base64
    - ``policy_encrypting_pubkey`` -- encoded as hex
    - ``alice_signing_pubkey`` -- encoded as hex

For more details on these arguments, see the nucypher documentation on the ``Alice.grant`` Python API method.

Bob
---

retrieve
~~~~~~~~

This endpoint controls the ``Bob.retrieve`` method.

- URL: ``/retrieve``
- HTTP Method: ``POST``
- Required arguments:
    - ``policy_encrypting_pubkey`` -- encoded as hex
    - ``alice_signing_pubkey`` -- encoded as hex
    - ``datasource_signing_pubkey`` -- encoded as hex
    - ``label`` -- encoded as base64
    - ``message_kit`` -- encoded as base64
- Returns: a JSON-array of base64-encoded decrypted plaintexts as ``plaintext``

For more details on these arguments, see the nucypher documentation on the ``Bob.retrieve`` Python API method.

Enrico (DataSource)
-------------------

encrypt_message
~~~~~~~~~~~~~~~

This endpoint controls the ``Enrico.encrypt_message`` method.

- URL: ``/encrypt_message``
- HTTP Method: ``POST``
- Required arguments:
    - ``message`` -- encoded as base64
- Returns: ``message_kit`` and ``signature`` encoded as base64

For more details on these arguments, see the nucypher documentation on the ``DataSource.encrypt_message`` Python API method.

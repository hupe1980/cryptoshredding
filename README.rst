
===============
CryptoShredding
===============

Crypto shredding is the practice of 'deleting' data through the destruction of the cryptographic keys protecting the data.

***************
Getting Started
***************

Required Prerequisites
======================

* Python 3.6+

Installation
============

.. note::

   If you have not already installed `cryptography`_, you might need to install additional
   prerequisites as detailed in the `cryptography installation guide`_ for your operating
   system.

   .. code::

       $ pip install cryptoshredding

*****
Usage
*****

KeyStore
========

.. code-block:: python

    >>> import boto3
    >>> from cryptoshredding import DynamodbKeyStore
    >>> from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
    >>>
    >>> aws_cmk_id = "arn:aws:kms:YOUR_KEY"
    >>> aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmk_id)
    >>>
    >>> table = boto3.resource("dynamodb").Table("key_store_table") 
    >>>
    >>> key_store = DynamodbKeyStore(table=table, materials_provider=aws_kms_cmp)
    >>>
    >>> key_store.create_key("foo")
    >>>
    >>> key_store.get_key("foo")
    >>>
    >>> key_store.delete_key("foo")

Dynamodb
========

.. code-block:: python

    >>> import boto3
    >>> from cryptoshredding.dynamodb import CryptoTable
    >>>
    >>> table = boto3.resource("dynamodb").Table("data_table") 
    >>>
    >>> crypto_table = CryptoTable(
    ...    table=table,
    ...    key_store=key_store,
    ...    attribute_actions=actions,
    ... )
    >>> crypto_table.put_item(key_id=key_id, Item=plaintext_item)
    >>>
    >>> encrypted_item = table.get_item(Key=index_key)["Item"]
    >>> decrypted_item = crypto_table.get_item(Key=index_key)["Item"]
    >>> decrypted_items = crypto_table.scan()["Items"]
    >>> 
    >>> encrypted = table.scan()
    >>> decrypted = crypto_table.scan()
    >>> 
    >>> assert encrypted["Count"] == 1
    >>> assert decrypted["Count"] == 1
    >>> assert len(encrypted["Items"]) == 1
    >>> assert len(decrypted["Items"]) == 1
    >>>
    >>> key_store.delete_key(key_id=key_id)  # shredding
    >>> 
    >>> encrypted = table.scan()
    >>> decrypted = crypto_table.scan()
    >>> 
    >>> assert encrypted["Count"] == 1
    >>> assert decrypted["Count"] == 0
    >>> assert len(encrypted["Items"]) == 1
    >>> assert len(decrypted["Items"]) == 0     

.. _cryptography: https://cryptography.io/en/latest/
.. _cryptography installation guide: https://cryptography.io/en/latest/installation.html
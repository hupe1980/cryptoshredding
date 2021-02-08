###############
CryptoShredding
###############

.. image:: https://img.shields.io/pypi/v/cryptoshredding.svg
   :target: https://pypi.python.org/pypi/cryptoshredding
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/cryptoshredding.svg
   :target: https://pypi.org/project/cryptoshredding
   :alt: Supported Python Versions

.. image:: https://github.com/hupe1980/cryptoshredding/workflows/ci/badge.svg
   :target: https://github.com/hupe1980/cryptoshredding/actions?query=workflow%3Aci
   :alt: ci

Crypto shredding is the practice of 'deleting' data through the destruction of the cryptographic keys protecting the data.

You can find the source on `GitHub`_.

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
    >>> key_store.create_main_key("foo")
    >>>
    >>> main_key = key_store.get_main_key("foo")
    >>>
    >>> key_store.delete_main_key("foo")  # shredding

MainKey
=======

.. code-block:: python

    >>> import boto3
    >>> from cryptoshredding import MainKey
    >>> 
    >>> main_key = key_store.get_main_key("foo")
    >>>
    >>> data_key, encrypted_data_key = main_key.generate_data_key()
    >>> 
    >>> decrypted_data_key = main_key.decrypt(encrypted_data_key)
    >>>
    >>> assert data_key == decrypted_data_key


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
    ... )
    >>> crypto_table.put_item(
    ...    CSEKeyId=key_id,
    ...    Item=plaintext_item
    ... )
    >>>
    >>> index_key = {"id": "foo"}
    >>> encrypted_item = table.get_item(Key=index_key)["Item"]
    >>> decrypted_item = crypto_table.get_item(Key=index_key)["Item"]
    >>> 
    >>> encrypted_items = table.scan()["Items"]
    >>> decrypted_items = crypto_table.scan()["Items"]
    >>> 
    >>> assert len(encrypted_items) == 1
    >>> assert len(decrypted_items) == 1
    >>>
    >>> key_store.delete_main_key(key_id)  # shredding
    >>> 
    >>> encrypted_items = table.scan()["Items"]
    >>> decrypted_items = crypto_table.scan()["Items"]
    >>> 
    >>> assert len(encrypted_items) == 1
    >>> assert len(decrypted_items) == 0  # !!!   

S3
==

.. code-block:: python

    >>> import boto3
    >>> from cryptoshredding.s3 import CryptoClient
    >>> 
    >>> s3 = boto3.client("s3", region_name="us-east-1")
    >>>
    >>> crypto_client = CryptoClient(
    ...    client=s3,
    ...    key_store=key_store,
    ... )
    >>> crypto_s3.put_object(
    ...    CSEKeyId=key_id,
    ...    Bucket=bucket.name,
    ...    Key="object",
    ...    Body="foo bar"",
    ... )
    >>> encrypted_obj = s3.get_object(
    ...    Bucket=bucket.name,
    ...    Key="object",
    ... )
    >>> decrypted_obj = crypto_s3.get_object(
    ...    Bucket=bucket.name,
    ...    Key="object",
    ... ) 

File
====

.. code-block:: python

    >>> from cryptoshredding.raw import CryptoFile
    >>> 
    >>> crypto_file = CryptoFile(
    ...    key_store=key_store,
    ... )
    >>> crypto_file.encrypt(
    ...    key_id=key_id,
    ...    plaintext_filename="plain.txt",
    ...    ciphertext_filename="cipher.txt"
    ... )
    >>> crypto_file.decrypt(
    ...    ciphertext_filename="cipher.txt",
    ...    plaintext_filename="decrypt.txt",
    ... )

Bytes
=====

.. code-block:: python

    >>> from cryptoshredding.raw import CryptoBytes
    >>> 
    >>> crypto_bytes = CryptoBytes(
    ...    key_store=key_store,
    ... )
    >>> encrypted, encrypted_header = crypto_bytes.encrypt(
    ...    key_id=key_id,
    ...    data=plain,
    ... )
    >>> decrypted, decrypted_header = crypto_bytes.decrypt(
    ...    data=encrypted,
    ... )

Kinesis
=======

Mongodb
=======

Sqlalchemy
==========

.. _cryptography: https://cryptography.io/en/latest/
.. _cryptography installation guide: https://cryptography.io/en/latest/installation.html
.. _GitHub: https://github.com/hupe1980/cryptoshredding/
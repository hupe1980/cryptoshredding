from typing import Dict, Optional, Text
from dynamodb_encryption_sdk.delegated_keys.jce import JceNameLocalDelegatedKey
from dynamodb_encryption_sdk.materials.wrapped import WrappedCryptographicMaterials
from dynamodb_encryption_sdk.identifiers import EncryptionKeyType, KeyEncodingType
from dynamodb_encryption_sdk.material_providers import CryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import EncryptionContext

from ..key_store import KeyStore


class KeyStoreMaterialsProvider(CryptographicMaterialsProvider):
    def __init__(
        self,
        key_store: KeyStore,
        material_description: Optional[Dict[Text, Text]] = None,
    ) -> None:
        if material_description is None:
            material_description = {}

        self._key_store = key_store
        self._material_description = material_description

    def _build_materials(
        self,
        encryption_context: EncryptionContext,
    ) -> WrappedCryptographicMaterials:
        """Construct
        :param EncryptionContext encryption_context: Encryption context for request
        :returns: Wrapped cryptographic materials
        :rtype: WrappedCryptographicMaterials
        """
        material_description = self._material_description.copy()
        material_description.update(encryption_context.material_description)

        key_bytes = self._key_store.get_key(material_description["key_id"])

        wrapping_key = JceNameLocalDelegatedKey(
            key=key_bytes,
            algorithm="AES",
            key_type=EncryptionKeyType.SYMMETRIC,
            key_encoding=KeyEncodingType.RAW,
        )
        signing_key = JceNameLocalDelegatedKey(
            key=key_bytes,
            algorithm="HmacSHA512",
            key_type=EncryptionKeyType.SYMMETRIC,
            key_encoding=KeyEncodingType.RAW,
        )
        return WrappedCryptographicMaterials(
            wrapping_key=wrapping_key,
            unwrapping_key=wrapping_key,
            signing_key=signing_key,
            material_description=material_description,
        )

    def encryption_materials(
        self,
        encryption_context: EncryptionContext
    ) -> WrappedCryptographicMaterials:
        """Provide encryption materials.
        :param EncryptionContext encryption_context: Encryption context for request
        :returns: Encryption materials
        :rtype: WrappedCryptographicMaterials
        """
        return self._build_materials(encryption_context)

    def decryption_materials(
        self,
        encryption_context: EncryptionContext
    ) -> WrappedCryptographicMaterials:
        """Provide decryption materials.
        :param EncryptionContext encryption_context: Encryption context for request
        :returns: Decryption materials
        :rtype: WrappedCryptographicMaterials
        """
        return self._build_materials(encryption_context)

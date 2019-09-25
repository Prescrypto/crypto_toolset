# -*- coding: utf-8 -*-

import os
import rsa
import pickle as cPickle  # nosec B403
import binascii
import base64
import logging
import random

# New cryptographic library
from Crypto.PublicKey import RSA  # nosec B413
from Crypto.Cipher import PKCS1_OAEP  # nosec B413
from Crypto.Hash import SHA256  # nosec B413
from Crypto.Signature import pkcs1_15  # nosec B413
''' The B413 error in Bandit about the use of the pycrypto library,
    but it also has the error B414 about the use of the pycryptodome
    library, so we must consider the change to the cryptography library
    from how Bandit recommended or ignored these errors.
'''


class CryptoTools(object):
    ''' Object tools for encrypt and decrypt info '''

    def __init__(self, has_legacy_keys=True, *args, **kwargs):
        # This number is the entropy created by the user in FE, your default
        # value is 161
        self.ENTROPY_NUMBER = self._number_random()
        self.logger = logging.getLogger('info')
        self.has_legacy_keys = has_legacy_keys

    def _number_random(self):
        '''Take a number between 180 to 220'''
        return random.randint(180, 220)  # nosec B311

    def bin2hex(self, binStr):
        '''convert str to hex '''
        binary_key = binascii.hexlify(binStr)
        return binary_key

    def hex2bin(self, hexStr):
        '''convert hex to str '''
        binary_key = binascii.unhexlify(hexStr)
        return binary_key

    def get_new_asym_keys(self, keysize=2048):
        ''' Return tuple of public and private key '''
        # LEGACY METHOD
        privatekey = RSA.generate(2048)
        publickey = privatekey.publickey()
        return (publickey, privatekey)

    def _get_new_asym_keys(self, keysize=512):
        ''' Return tuple of public and private key '''
        # LEGACY METHOD
        return rsa.newkeys(keysize)

    def get_pem_priv_format(self, EncryptionPrivateKey):
        ''' return priv key on pem format '''
        if self.has_legacy_keys:
            return EncryptionPrivateKey.save_pkcs1(format="PEM")
        else:
            return EncryptionPrivateKey.exportKey('PEM')

    def savify_key(self, EncryptionKeyObject):
        ''' Give it a key, returns a hex string ready to save '''
        if self.has_legacy_keys:
            return self._savify_key(EncryptionKeyObject)
        else:
            pickld_key = EncryptionKeyObject.exportKey('PEM')
            return self.bin2hex(pickld_key)

    def _savify_key(self, EncryptionKeyObject):
        ''' Give it a key, returns a hex string ready to save '''
        # LEGAY METHOD
        pickld_key = cPickle.dumps(EncryptionKeyObject)
        return self.bin2hex(pickld_key)

    def un_savify_key(self, HexPickldKey):
        ''' Give it a hex saved string, returns a Key object ready to use'''
        if self.has_legacy_keys:
            return self._un_savify_key(HexPickldKey)
        else:
            bin_str_key = self.hex2bin(HexPickldKey)
            # return objetc of RSA type
            return RSA.importKey(bin_str_key)

    def _un_savify_key(self, HexPickldKey):
        ''' Give it a hex saved string, returns a Key object ready to use '''
        # LEGACY METHOD
        bin_str_key = self.hex2bin(HexPickldKey)
        return cPickle.loads(bin_str_key)  # nosec B301

    def encrypt_with_public_key(self, message, EncryptionPublicKey):
        ''' Encrypt with PublicKey object '''
        if self.has_legacy_keys:
            return self._encrypt_with_public_key(message, EncryptionPublicKey)
        else:
            encrypt_rsa = PKCS1_OAEP.new(EncryptionPublicKey)
            encryptedtext = encrypt_rsa.encrypt(message)
            return encryptedtext

    def _encrypt_with_public_key(self, message, EncryptionPublicKey):
        ''' Encrypt with PublicKey object '''
        # LEGACY METHOD
        encryptedtext = rsa.encrypt(message, EncryptionPublicKey)
        return encryptedtext

    def decrypt_with_private_key(self, encryptedtext, EncryptionPrivateKey):
        ''' Decrypt with PrivateKey object '''
        if self.has_legacy_keys:
            return self._decrypt_with_private_key(encryptedtext, EncryptionPrivateKey)
        else:
            decrypt_rsa = PKCS1_OAEP.new(EncryptionPrivateKey)
            message = decrypt_rsa.decrypt(encryptedtext)
            return message

    def _decrypt_with_private_key(self, encryptedtext, EncryptionPrivateKey):
        ''' Decrypt with PrivateKey object '''
        # LEGACY METHOD
        message = rsa.decrypt(encryptedtext, EncryptionPrivateKey)
        return message

    def sign(self, message, PrivateKey):
        ''' Sign a message '''
        if self.has_legacy_keys:
            return self._sign(message, PrivateKey)
        else:
            message_hash = SHA256.new(message.encode())
            signature = pkcs1_15.new(PrivateKey).sign(message_hash)
            return base64.b64encode(signature)

    def _sign(self, message, PrivateKey):
        ''' Sign a message '''
        # LEGACY METHOD
        signature = rsa.sign(message, PrivateKey, 'SHA-1')
        return base64.b64encode(signature)

    def verify(self, message, signature, PublicKey):
        '''Verify if a signed message is valid'''
        message = message.encode()
        if self.has_legacy_keys:
            return self._verify(message, signature, PublicKey)
        else:
            signature = base64.b64decode(signature)
            message_hash = SHA256.new(message)
            try:
                pkcs1_15.new(PublicKey).verify(message_hash, signature)
                return True
            except:  # noqa: noqa: E722
                self.logger.error(
                    "[CryptoTool, verify ERROR ] Signature or message are corrupted")
                return False

    def _verify(self, message, signature, PublicKey):
        '''Verify if a signed message is valid '''
        # LEGACY METHOD
        signature = base64.b64decode(signature)
        try:
            return rsa.verify(message, signature, PublicKey)
        except:  # noqa: E722
            self.logger.error(
                "[CryptoTool, verify ERROR ] Signature or message are corrupted")
            return False

    def entropy(self, number):
        '''This method verify if entropy is enough'''
        if self.ENTROPY_NUMBER > 160:
            return os.urandom(self.ENTROPY_NUMBER)
        else:
            raise ValueError('Error')

    def create_key_with_entropy(self):
        '''This method create a pair RSA keys with entropy created by the user in FE'''
        try:
            privatekey = RSA.generate(2048, randfunc=self.entropy)
        except Exception as e:
            self.logger.error('{}'.format(e))
            self.logger.error(
                "[CryptoTool, create_key_with_entropy ERROR] Entropy not enough")
            privatekey = None

        if privatekey is None:
            publickey = None
        else:
            publickey = privatekey.publickey()

        return (publickey, privatekey)

    def fiel_to_rsakeys(directory_file, password):
        '''This method generates your private key and public key in pem format
        from your FIEL file in key format
        directorty_file: Only copy the direction file without extension, i.e.,
        wihtout .key
        password: enter password of your FIEL
        '''
        privatekey = None
        with open(directory_file + '.key', 'rb') as file:
            privatekey = RSA.import_key(file.read(), passphrase=password)

        publickey = privatekey.publickey()
        return (publickey, privatekey)

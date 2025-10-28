"""
Secure Credentials Storage
Uses system keyring and encryption for sensitive data
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
from loguru import logger

from core.exceptions import SystemError, ValidationError


class SecretsManager:
    """
    Secure credential storage using system keyring

    Features:
    - System keyring integration
    - Encryption for sensitive data
    - No plaintext passwords in config files
    - Safe credential retrieval

    Example:
        manager = SecretsManager()

        # Store credential
        manager.store_credential("myapp", "username", "password")

        # Retrieve credential
        password = manager.get_credential("myapp", "username")

        # Encrypt sensitive data
        encrypted = manager.encrypt("secret data")
        decrypted = manager.decrypt(encrypted)
    """

    def __init__(self, app_name: str = "webtestool"):
        """
        Initialize secrets manager

        Args:
            app_name: Application name for keyring
        """
        self.app_name = app_name
        self._cipher = None
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption cipher"""
        try:
            # Try to use system keyring
            import keyring

            # Get or create encryption key
            key = keyring.get_password(self.app_name, "encryption_key")

            if not key:
                # Generate new key
                key = Fernet.generate_key().decode()
                keyring.set_password(self.app_name, "encryption_key", key)
                logger.info("Generated new encryption key")

            self._cipher = Fernet(key.encode())
            logger.debug("Encryption initialized")

        except ImportError:
            logger.warning("Keyring not available, using fallback encryption")
            self._init_fallback_encryption()

        except Exception as e:
            logger.warning(f"Failed to use system keyring: {e}")
            self._init_fallback_encryption()

    def _init_fallback_encryption(self):
        """Initialize fallback encryption (file-based)"""
        key_file = Path.home() / f".{self.app_name}" / "encryption.key"
        key_file.parent.mkdir(exist_ok=True, mode=0o700)

        if key_file.exists():
            key = key_file.read_bytes()
        else:
            # Generate new key
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Read/write for owner only
            logger.info(f"Generated new encryption key: {key_file}")

        self._cipher = Fernet(key)

    def encrypt(self, value: str) -> str:
        """
        Encrypt a string value

        Args:
            value: Value to encrypt

        Returns:
            Encrypted value (base64 encoded)
        """
        if not isinstance(value, str):
            value = str(value)

        try:
            encrypted = self._cipher.encrypt(value.encode())
            return encrypted.decode()
        except Exception as e:
            raise SystemError(
                f"Encryption failed: {str(e)}",
                details={'error': str(e)},
                original_error=e
            )

    def decrypt(self, encrypted_value: str) -> str:
        """
        Decrypt an encrypted value

        Args:
            encrypted_value: Encrypted value

        Returns:
            Decrypted value
        """
        if not isinstance(encrypted_value, str):
            raise ValidationError(
                "Encrypted value must be a string",
                details={'type': type(encrypted_value).__name__}
            )

        try:
            decrypted = self._cipher.decrypt(encrypted_value.encode())
            return decrypted.decode()
        except Exception as e:
            raise SystemError(
                f"Decryption failed: {str(e)}",
                details={'error': str(e)},
                suggestion="Value may be corrupted or not encrypted",
                original_error=e
            )

    def store_credential(
        self,
        service: str,
        username: str,
        password: str
    ):
        """
        Store credential in system keyring

        Args:
            service: Service name
            username: Username
            password: Password
        """
        try:
            import keyring

            service_name = f"{self.app_name}:{service}"
            keyring.set_password(service_name, username, password)
            logger.info(f"Stored credential for {service}/{username}")

        except ImportError:
            # Fallback to encrypted file storage
            self._store_credential_file(service, username, password)

        except Exception as e:
            logger.error(f"Failed to store credential: {e}")
            # Fallback to encrypted file storage
            self._store_credential_file(service, username, password)

    def get_credential(
        self,
        service: str,
        username: str
    ) -> Optional[str]:
        """
        Retrieve credential from system keyring

        Args:
            service: Service name
            username: Username

        Returns:
            Password or None if not found
        """
        try:
            import keyring

            service_name = f"{self.app_name}:{service}"
            password = keyring.get_password(service_name, username)

            if password:
                logger.debug(f"Retrieved credential for {service}/{username}")
                return password

        except ImportError:
            # Try encrypted file storage
            return self._get_credential_file(service, username)

        except Exception as e:
            logger.error(f"Failed to retrieve credential: {e}")
            # Try encrypted file storage
            return self._get_credential_file(service, username)

        # Not found in keyring, try file
        return self._get_credential_file(service, username)

    def delete_credential(self, service: str, username: str):
        """
        Delete credential from keyring

        Args:
            service: Service name
            username: Username
        """
        try:
            import keyring

            service_name = f"{self.app_name}:{service}"
            keyring.delete_password(service_name, username)
            logger.info(f"Deleted credential for {service}/{username}")

        except Exception as e:
            logger.warning(f"Failed to delete credential: {e}")

        # Also try to delete from file storage
        self._delete_credential_file(service, username)

    def _get_credentials_file(self) -> Path:
        """Get path to credentials file"""
        creds_file = Path.home() / f".{self.app_name}" / "credentials.enc"
        creds_file.parent.mkdir(exist_ok=True, mode=0o700)
        return creds_file

    def _load_credentials_file(self) -> Dict[str, Dict[str, str]]:
        """Load credentials from encrypted file"""
        creds_file = self._get_credentials_file()

        if not creds_file.exists():
            return {}

        try:
            encrypted_data = creds_file.read_text()
            decrypted_data = self.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Failed to load credentials file: {e}")
            return {}

    def _save_credentials_file(self, credentials: Dict[str, Dict[str, str]]):
        """Save credentials to encrypted file"""
        creds_file = self._get_credentials_file()

        try:
            json_data = json.dumps(credentials, indent=2)
            encrypted_data = self.encrypt(json_data)
            creds_file.write_text(encrypted_data)
            creds_file.chmod(0o600)  # Read/write for owner only
        except Exception as e:
            logger.error(f"Failed to save credentials file: {e}")
            raise

    def _store_credential_file(
        self,
        service: str,
        username: str,
        password: str
    ):
        """Store credential in encrypted file (fallback)"""
        credentials = self._load_credentials_file()

        if service not in credentials:
            credentials[service] = {}

        credentials[service][username] = password
        self._save_credentials_file(credentials)
        logger.info(f"Stored credential in file for {service}/{username}")

    def _get_credential_file(
        self,
        service: str,
        username: str
    ) -> Optional[str]:
        """Get credential from encrypted file (fallback)"""
        credentials = self._load_credentials_file()

        if service in credentials and username in credentials[service]:
            logger.debug(f"Retrieved credential from file for {service}/{username}")
            return credentials[service][username]

        return None

    def _delete_credential_file(self, service: str, username: str):
        """Delete credential from encrypted file"""
        credentials = self._load_credentials_file()

        if service in credentials and username in credentials[service]:
            del credentials[service][username]

            # Remove service if empty
            if not credentials[service]:
                del credentials[service]

            self._save_credentials_file(credentials)
            logger.info(f"Deleted credential from file for {service}/{username}")

    def resolve_secret(self, value: str) -> str:
        """
        Resolve secret reference in configuration

        Supports formats:
        - {{ SECRET:service:username }} - Retrieve from keyring
        - {{ ENCRYPT:plaintext }} - Encrypt and return
        - {{ DECRYPT:encrypted }} - Decrypt and return

        Args:
            value: Value that may contain secret reference

        Returns:
            Resolved value
        """
        if not isinstance(value, str):
            return value

        # {{ SECRET:service:username }}
        secret_pattern = r'\{\{\s*SECRET:([^:]+):([^}]+)\s*\}\}'
        match = re.search(secret_pattern, value)
        if match:
            service, username = match.groups()
            password = self.get_credential(service, username)

            if password:
                return value.replace(match.group(0), password)
            else:
                logger.warning(f"Secret not found: {service}/{username}")
                return value

        # {{ ENCRYPT:plaintext }}
        encrypt_pattern = r'\{\{\s*ENCRYPT:([^}]+)\s*\}\}'
        match = re.search(encrypt_pattern, value)
        if match:
            plaintext = match.group(1)
            encrypted = self.encrypt(plaintext)
            return value.replace(match.group(0), encrypted)

        # {{ DECRYPT:encrypted }}
        decrypt_pattern = r'\{\{\s*DECRYPT:([^}]+)\s*\}\}'
        match = re.search(decrypt_pattern, value)
        if match:
            encrypted = match.group(1)
            try:
                decrypted = self.decrypt(encrypted)
                return value.replace(match.group(0), decrypted)
            except Exception as e:
                logger.error(f"Failed to decrypt: {e}")
                return value

        return value


# Import for pattern matching
import re


# Singleton instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(app_name: str = "webtestool") -> SecretsManager:
    """
    Get or create singleton secrets manager

    Args:
        app_name: Application name

    Returns:
        SecretsManager instance
    """
    global _secrets_manager

    if _secrets_manager is None:
        _secrets_manager = SecretsManager(app_name)

    return _secrets_manager


# CLI commands for credential management

def store_credential_cli():
    """CLI command to store credential"""
    import getpass

    print("Store Credential")
    print("=" * 50)

    service = input("Service name: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    if not service or not username or not password:
        print("❌ All fields are required")
        return

    manager = get_secrets_manager()
    manager.store_credential(service, username, password)
    print(f"✅ Credential stored for {service}/{username}")


def get_credential_cli():
    """CLI command to retrieve credential"""
    print("Get Credential")
    print("=" * 50)

    service = input("Service name: ").strip()
    username = input("Username: ").strip()

    if not service or not username:
        print("❌ Service and username are required")
        return

    manager = get_secrets_manager()
    password = manager.get_credential(service, username)

    if password:
        print(f"✅ Password: {password}")
    else:
        print(f"❌ Credential not found for {service}/{username}")


if __name__ == "__main__":
    # Test
    manager = SecretsManager()

    # Test encryption
    encrypted = manager.encrypt("Hello World!")
    decrypted = manager.decrypt(encrypted)
    assert decrypted == "Hello World!"

    print("✅ Encryption test passed")

    # Test credential storage
    manager.store_credential("test", "testuser", "testpass")
    password = manager.get_credential("test", "testuser")
    assert password == "testpass"

    print("✅ Credential storage test passed")

    # Clean up
    manager.delete_credential("test", "testuser")

    print("✅ All tests passed")

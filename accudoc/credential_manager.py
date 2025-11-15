"""
Credential management module for AccuDoc.

Provides secure storage and retrieval of Git credentials:
- Encrypted credential storage
- Support for passwords and tokens
- SSH key management
- Credential validation
"""

import json
import logging
import base64
from typing import Dict, Optional, Any
from pathlib import Path
import os
import stat

# Try to import cryptography for encryption
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class CredentialManager:
    """Manage secure storage of Git credentials."""
    
    def __init__(self, storage_path: Optional[Path] = None, password: Optional[str] = None):
        """
        Initialize credential manager.
        
        Args:
            storage_path: Path to credential storage file (default: ~/.accudoc/credentials.enc)
            password: Master password for encryption (prompts if not provided)
        """
        if storage_path is None:
            storage_path = Path.home() / '.accudoc' / 'credentials.enc'
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('accudoc.credentials')
        
        if CRYPTO_AVAILABLE and password:
            self.cipher = self._create_cipher(password)
        else:
            self.cipher = None
            if not CRYPTO_AVAILABLE:
                self.logger.warning("cryptography not available, credentials will be stored unencrypted")
        
        # Set secure file permissions
        self._set_secure_permissions()
    
    def _create_cipher(self, password: str):
        """
        Create cipher for encryption/decryption.
        
        Args:
            password: Master password
            
        Returns:
            Fernet cipher instance
        """
        # Derive key from password
        salt = b'accudoc_salt_v1'  # Static salt (consider user-specific in production)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def _set_secure_permissions(self):
        """Set secure file permissions (user read/write only)."""
        if self.storage_path.exists():
            # Set to 0600 (rw-------)
            self.storage_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    
    def _load_storage(self) -> Dict[str, Any]:
        """
        Load credentials from storage.
        
        Returns:
            Dictionary of credentials
        """
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, 'rb') as f:
                data = f.read()
            
            if self.cipher and data:
                # Decrypt
                decrypted = self.cipher.decrypt(data)
                return json.loads(decrypted.decode())
            else:
                # Unencrypted fallback
                return json.loads(data.decode()) if data else {}
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")
            return {}
    
    def _save_storage(self, credentials: Dict[str, Any]):
        """
        Save credentials to storage.
        
        Args:
            credentials: Dictionary of credentials to save
        """
        try:
            data = json.dumps(credentials, indent=2).encode()
            
            if self.cipher:
                # Encrypt
                encrypted = self.cipher.encrypt(data)
                with open(self.storage_path, 'wb') as f:
                    f.write(encrypted)
            else:
                # Unencrypted fallback
                with open(self.storage_path, 'wb') as f:
                    f.write(data)
            
            # Ensure secure permissions
            self._set_secure_permissions()
            
        except Exception as e:
            self.logger.error(f"Error saving credentials: {e}")
    
    def store_password(self, host: str, username: str, password: str):
        """
        Store password credential.
        
        Args:
            host: Git host (e.g., 'github.com')
            username: Username
            password: Password or personal access token
        """
        credentials = self._load_storage()
        
        if host not in credentials:
            credentials[host] = {}
        
        credentials[host][username] = {
            'type': 'password',
            'password': password
        }
        
        self._save_storage(credentials)
        self.logger.info(f"Stored credential for {username}@{host}")
    
    def store_token(self, host: str, token: str, token_type: str = 'personal'):
        """
        Store access token.
        
        Args:
            host: Git host
            token: Access token
            token_type: Type of token (personal, oauth, etc.)
        """
        credentials = self._load_storage()
        
        if host not in credentials:
            credentials[host] = {}
        
        credentials[host]['_token'] = {
            'type': 'token',
            'token': token,
            'token_type': token_type
        }
        
        self._save_storage(credentials)
        self.logger.info(f"Stored {token_type} token for {host}")
    
    def get_credential(self, host: str, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get credential for host.
        
        Args:
            host: Git host
            username: Optional username (if None, returns token if available)
            
        Returns:
            Credential dictionary or None
        """
        credentials = self._load_storage()
        
        if host not in credentials:
            return None
        
        if username:
            return credentials[host].get(username)
        else:
            # Return token if available
            return credentials[host].get('_token')
    
    def list_credentials(self) -> Dict[str, list]:
        """
        List all stored credentials.
        
        Returns:
            Dictionary mapping hosts to list of usernames
        """
        credentials = self._load_storage()
        result = {}
        
        for host, creds in credentials.items():
            result[host] = [u for u in creds.keys() if not u.startswith('_')]
        
        return result
    
    def delete_credential(self, host: str, username: Optional[str] = None):
        """
        Delete credential.
        
        Args:
            host: Git host
            username: Username (if None, deletes token)
        """
        credentials = self._load_storage()
        
        if host in credentials:
            if username:
                if username in credentials[host]:
                    del credentials[host][username]
                    self.logger.info(f"Deleted credential for {username}@{host}")
            else:
                # Delete token
                if '_token' in credentials[host]:
                    del credentials[host]['_token']
                    self.logger.info(f"Deleted token for {host}")
            
            # Remove host if empty
            if not credentials[host]:
                del credentials[host]
            
            self._save_storage(credentials)
    
    def clear_all(self):
        """Clear all stored credentials."""
        if self.storage_path.exists():
            self.storage_path.unlink()
            self.logger.info("Cleared all credentials")


class SSHKeyManager:
    """Manage SSH keys for Git operations."""
    
    def __init__(self, ssh_dir: Optional[Path] = None):
        """
        Initialize SSH key manager.
        
        Args:
            ssh_dir: SSH directory (default: ~/.ssh)
        """
        if ssh_dir is None:
            ssh_dir = Path.home() / '.ssh'
        
        self.ssh_dir = Path(ssh_dir)
        self.logger = logging.getLogger('accudoc.ssh_keys')
    
    def list_keys(self) -> list:
        """
        List available SSH keys.
        
        Returns:
            List of key file paths
        """
        if not self.ssh_dir.exists():
            return []
        
        keys = []
        for file in self.ssh_dir.iterdir():
            if file.is_file() and not file.name.endswith('.pub'):
                # Check if it's a private key
                if file.stat().st_size > 0:
                    keys.append(str(file))
        
        return sorted(keys)
    
    def has_key(self, key_name: str = 'id_rsa') -> bool:
        """
        Check if SSH key exists.
        
        Args:
            key_name: Key file name
            
        Returns:
            True if key exists
        """
        key_path = self.ssh_dir / key_name
        return key_path.exists()
    
    def get_key_path(self, key_name: str = 'id_rsa') -> Optional[Path]:
        """
        Get path to SSH key.
        
        Args:
            key_name: Key file name
            
        Returns:
            Path to key file or None
        """
        key_path = self.ssh_dir / key_name
        if key_path.exists():
            return key_path
        return None
    
    def get_public_key(self, key_name: str = 'id_rsa') -> Optional[str]:
        """
        Get public key content.
        
        Args:
            key_name: Key file name
            
        Returns:
            Public key content or None
        """
        pub_key_path = self.ssh_dir / f'{key_name}.pub'
        
        if pub_key_path.exists():
            try:
                return pub_key_path.read_text().strip()
            except Exception as e:
                self.logger.error(f"Error reading public key: {e}")
        
        return None
    
    def configure_git_ssh(self, key_name: str = 'id_rsa') -> Optional[str]:
        """
        Configure Git to use specific SSH key.
        
        Args:
            key_name: Key file name
            
        Returns:
            SSH command string for Git or None
        """
        key_path = self.get_key_path(key_name)
        
        if key_path:
            # Return GIT_SSH_COMMAND format
            return f'ssh -i {key_path} -o IdentitiesOnly=yes'
        
        return None


def get_credential_from_env(host: str) -> Optional[Dict[str, str]]:
    """
    Get credential from environment variables.
    
    Args:
        host: Git host
        
    Returns:
        Credential dictionary or None
    """
    # Check for host-specific token
    env_var = f'{host.upper().replace(".", "_")}_TOKEN'
    token = os.getenv(env_var)
    
    if token:
        return {
            'type': 'token',
            'token': token,
            'source': 'environment'
        }
    
    # Check for generic tokens
    for var in ['GIT_TOKEN', 'GITHUB_TOKEN', 'GITLAB_TOKEN']:
        token = os.getenv(var)
        if token:
            return {
                'type': 'token',
                'token': token,
                'source': 'environment'
            }
    
    return None

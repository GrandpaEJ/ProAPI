"""
Port forwarding module for ProAPI framework.

Provides functionality to expose local servers to the internet.
"""

import json
import os
import random
import socket
import string
import subprocess
import sys
import threading
import time
from typing import Dict, Optional, Tuple, Union

from .logging import app_logger

class PortForwarder:
    """
    Base class for port forwarders.
    """

    def __init__(self, local_port: int, local_host: str = "127.0.0.1"):
        """
        Initialize the port forwarder.

        Args:
            local_port: Local port to forward
            local_host: Local host to forward from
        """
        self.local_port = local_port
        self.local_host = local_host
        self.public_url = None
        self.process = None
        self.active = False
        self.error = None

    def start(self) -> bool:
        """
        Start the port forwarder.

        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement start()")

    def stop(self) -> bool:
        """
        Stop the port forwarder.

        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement stop()")

    def get_public_url(self) -> Optional[str]:
        """
        Get the public URL.

        Returns:
            Public URL or None if not available
        """
        return self.public_url

class NgrokForwarder(PortForwarder):
    """
    Port forwarder using ngrok.
    """

    def __init__(self, local_port: int, local_host: str = "127.0.0.1", auth_token: Optional[str] = None):
        """
        Initialize the ngrok forwarder.

        Args:
            local_port: Local port to forward
            local_host: Local host to forward from
            auth_token: Ngrok auth token (optional)
        """
        super().__init__(local_port, local_host)
        self.auth_token = auth_token
        self._api_url = "http://127.0.0.1:4040/api/tunnels"
        self._check_thread = None

    def _is_ngrok_installed(self) -> bool:
        """
        Check if ngrok is installed.

        Returns:
            True if ngrok is installed, False otherwise
        """
        try:
            # Check if ngrok is in PATH
            if sys.platform == "win32":
                result = subprocess.run(["where", "ngrok"], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "ngrok"], capture_output=True, text=True)

            return result.returncode == 0
        except Exception:
            return False

    def _install_ngrok(self) -> bool:
        """
        Install ngrok.

        Returns:
            True if successful, False otherwise
        """
        print("Ngrok is not installed. Attempting to install...")

        try:
            if sys.platform == "win32":
                # Windows installation
                import urllib.request
                import zipfile

                # Download ngrok
                url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
                zip_path = os.path.join(os.path.expanduser("~"), "ngrok.zip")

                print("Downloading ngrok...")
                urllib.request.urlretrieve(url, zip_path)

                # Extract ngrok
                ngrok_dir = os.path.join(os.path.expanduser("~"), ".ngrok")
                os.makedirs(ngrok_dir, exist_ok=True)

                print("Extracting ngrok...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(ngrok_dir)

                # Add to PATH
                os.environ["PATH"] += os.pathsep + ngrok_dir

                # Clean up
                os.remove(zip_path)

                print("Ngrok installed successfully.")
                return True
            else:
                # Linux/Mac installation
                app_logger.warning("Please install ngrok manually:")
                app_logger.warning("  - Download from https://ngrok.com/download")
                app_logger.warning("  - Extract and add to your PATH")
                return False
        except Exception as e:
            app_logger.error(f"Error installing ngrok: {e}")
            return False

    def _get_tunnel_url(self) -> Optional[str]:
        """
        Get the tunnel URL from the ngrok API.

        Returns:
            Tunnel URL or None if not available
        """
        import urllib.request
        import urllib.error

        try:
            # Get tunnels from ngrok API
            with urllib.request.urlopen(self._api_url) as response:
                data = json.loads(response.read().decode())

                # Find the HTTP tunnel
                for tunnel in data.get("tunnels", []):
                    if tunnel.get("proto") == "https":
                        return tunnel.get("public_url")

                return None
        except (urllib.error.URLError, json.JSONDecodeError):
            return None

    def _check_tunnel_status(self):
        """Check tunnel status periodically."""
        while self.active:
            url = self._get_tunnel_url()
            if url:
                self.public_url = url
                print(f"Public URL: {self.public_url}")
                break

            time.sleep(1)

    def start(self) -> bool:
        """
        Start the ngrok forwarder.

        Returns:
            True if successful, False otherwise
        """
        # Check if ngrok is installed
        if not self._is_ngrok_installed():
            if not self._install_ngrok():
                self.error = "Ngrok is not installed and could not be installed automatically."
                return False

        try:
            # Build command
            cmd = ["ngrok", "http", f"{self.local_host}:{self.local_port}"]

            # Add auth token if provided
            if self.auth_token:
                cmd.extend(["--authtoken", self.auth_token])

            # Start ngrok process
            if sys.platform == "win32":
                # Hide console window on Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo
                )
            else:
                # Redirect output to /dev/null on Unix
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Mark as active
            self.active = True

            # Start checking for tunnel URL
            self._check_thread = threading.Thread(target=self._check_tunnel_status)
            self._check_thread.daemon = True
            self._check_thread.start()

            # Wait for tunnel to be established
            for _ in range(10):
                if self.public_url:
                    return True
                time.sleep(1)

            # If we get here, the tunnel was not established in time
            if not self.public_url:
                self.error = "Timeout waiting for ngrok tunnel to be established."
                self.stop()
                return False

            return True
        except Exception as e:
            self.error = f"Error starting ngrok: {e}"
            return False

    def stop(self) -> bool:
        """
        Stop the ngrok forwarder.

        Returns:
            True if successful, False otherwise
        """
        if self.process:
            self.active = False
            self.process.terminate()
            self.process = None
            self.public_url = None
            return True

        return False

class CloudflareForwarder(PortForwarder):
    """
    Port forwarder using Cloudflare Tunnel (cloudflared).
    """

    def __init__(self, local_port: int, local_host: str = "127.0.0.1", tunnel_name: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize the Cloudflare Tunnel forwarder.

        Args:
            local_port: Local port to forward
            local_host: Local host to forward from
            tunnel_name: Name for the tunnel (optional)
            token: Cloudflare Tunnel token (optional)
        """
        super().__init__(local_port, local_host)
        self.tunnel_name = tunnel_name or self._generate_tunnel_name()
        self.token = token
        self._output_thread = None

    def _generate_tunnel_name(self) -> str:
        """
        Generate a random tunnel name.

        Returns:
            Random tunnel name
        """
        # Generate a random 8-character name
        chars = string.ascii_lowercase + string.digits
        return "proapi-" + "".join(random.choice(chars) for _ in range(8))

    def _is_cloudflared_installed(self) -> bool:
        """
        Check if cloudflared is installed.

        Returns:
            True if cloudflared is installed, False otherwise
        """
        try:
            # Check if cloudflared is in PATH
            if sys.platform == "win32":
                result = subprocess.run(["where", "cloudflared"], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "cloudflared"], capture_output=True, text=True)

            return result.returncode == 0
        except Exception:
            return False

    def _install_cloudflared(self) -> bool:
        """
        Install cloudflared.

        Returns:
            True if successful, False otherwise
        """
        print("Cloudflared is not installed. Attempting to install...")

        try:
            if sys.platform == "win32":
                # Windows installation
                import urllib.request
                import zipfile

                # Download cloudflared
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
                exe_path = os.path.join(os.path.expanduser("~"), ".cloudflared", "cloudflared.exe")

                # Create directory
                os.makedirs(os.path.dirname(exe_path), exist_ok=True)

                print("Downloading cloudflared...")
                urllib.request.urlretrieve(url, exe_path)

                # Add to PATH
                os.environ["PATH"] += os.pathsep + os.path.dirname(exe_path)

                print("Cloudflared installed successfully.")
                return True
            elif sys.platform == "darwin":
                # macOS installation
                print("Installing cloudflared via Homebrew...")
                subprocess.run(["brew", "install", "cloudflare/cloudflare/cloudflared"], check=True)
                print("Cloudflared installed successfully.")
                return True
            else:
                # Linux installation
                app_logger.warning("Please install cloudflared manually:")
                app_logger.warning("  - Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation")
                app_logger.warning("  - Extract and add to your PATH")
                return False
        except Exception as e:
            app_logger.error(f"Error installing cloudflared: {e}")
            return False

    def _process_output(self):
        """
        Process the output from the cloudflared process.
        """
        while self.active and self.process:
            line = self.process.stdout.readline().decode().strip()
            if not line:
                continue

            print(f"Cloudflared: {line}")

            # Look for the URL in the output
            if "https://" in line and ".trycloudflare.com" in line:
                # Extract the URL
                words = line.split()
                for word in words:
                    if word.startswith("https://") and ".trycloudflare.com" in word:
                        self.public_url = word
                        print(f"Public URL: {self.public_url}")
                        break

            # Check for errors
            if "error" in line.lower():
                self.error = line
                print(f"Cloudflare error: {line}")

    def start(self) -> bool:
        """
        Start the Cloudflare Tunnel forwarder.

        Returns:
            True if successful, False otherwise
        """
        # Check if cloudflared is installed
        if not self._is_cloudflared_installed():
            if not self._install_cloudflared():
                self.error = "Cloudflared is not installed and could not be installed automatically."
                return False

        try:
            # Build command for quick tunnel (no account required)
            cmd = ["cloudflared", "tunnel", "--url", f"http://{self.local_host}:{self.local_port}"]

            # Add name if provided
            if self.tunnel_name:
                cmd.extend(["--name", self.tunnel_name])

            # If token is provided, use it for authenticated tunnel
            if self.token:
                cmd = ["cloudflared", "tunnel", "run", "--token", self.token]

            # Start cloudflared process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=False,
                bufsize=1
            )

            # Mark as active
            self.active = True

            # Start processing output
            self._output_thread = threading.Thread(target=self._process_output)
            self._output_thread.daemon = True
            self._output_thread.start()

            # Wait for tunnel to be established
            for _ in range(20):  # Longer timeout for Cloudflare
                if self.public_url:
                    return True
                time.sleep(1)

            # If we get here, the tunnel was not established in time
            if not self.public_url:
                self.error = "Timeout waiting for Cloudflare Tunnel to be established."
                self.stop()
                return False

            return True
        except Exception as e:
            self.error = f"Error starting Cloudflare Tunnel: {e}"
            return False

    def stop(self) -> bool:
        """
        Stop the Cloudflare Tunnel forwarder.

        Returns:
            True if successful, False otherwise
        """
        if self.process:
            self.active = False
            self.process.terminate()
            self.process = None
            self.public_url = None
            return True

        return False

class LocalTunnelForwarder(PortForwarder):
    """
    Port forwarder using localtunnel.
    """

    def __init__(self, local_port: int, local_host: str = "127.0.0.1", subdomain: Optional[str] = None):
        """
        Initialize the localtunnel forwarder.

        Args:
            local_port: Local port to forward
            local_host: Local host to forward from
            subdomain: Subdomain to use (optional)
        """
        super().__init__(local_port, local_host)
        self.subdomain = subdomain or self._generate_subdomain()
        self._output_thread = None

    def _generate_subdomain(self) -> str:
        """
        Generate a random subdomain.

        Returns:
            Random subdomain
        """
        # Generate a random 8-character subdomain
        chars = string.ascii_lowercase + string.digits
        return "proapi-" + "".join(random.choice(chars) for _ in range(8))

    def _is_lt_installed(self) -> bool:
        """
        Check if localtunnel is installed.

        Returns:
            True if localtunnel is installed, False otherwise
        """
        try:
            # Check if lt is in PATH
            if sys.platform == "win32":
                result = subprocess.run(["where", "lt"], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "lt"], capture_output=True, text=True)

            return result.returncode == 0
        except Exception:
            return False

    def _install_lt(self) -> bool:
        """
        Install localtunnel.

        Returns:
            True if successful, False otherwise
        """
        print("Localtunnel is not installed. Attempting to install...")

        try:
            # Check if npm is installed
            if sys.platform == "win32":
                result = subprocess.run(["where", "npm"], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "npm"], capture_output=True, text=True)

            if result.returncode != 0:
                app_logger.warning("npm is not installed. Please install Node.js and npm first.")
                return False

            # Install localtunnel
            app_logger.info("Installing localtunnel...")
            subprocess.run(["npm", "install", "-g", "localtunnel"], check=True)

            app_logger.success("Localtunnel installed successfully.")
            return True
        except Exception as e:
            app_logger.error(f"Error installing localtunnel: {e}")
            return False

    def _process_output(self):
        """Process the output from the localtunnel process."""
        while self.active and self.process:
            line = self.process.stdout.readline().decode().strip()
            if not line:
                continue

            # Look for the URL in the output
            if "your url is:" in line.lower():
                self.public_url = line.split("your url is:")[-1].strip()
                print(f"Public URL: {self.public_url}")

            # Check for errors
            if "error" in line.lower():
                self.error = line
                print(f"Localtunnel error: {line}")

    def start(self) -> bool:
        """
        Start the localtunnel forwarder.

        Returns:
            True if successful, False otherwise
        """
        # Check if localtunnel is installed
        if not self._is_lt_installed():
            if not self._install_lt():
                self.error = "Localtunnel is not installed and could not be installed automatically."
                return False

        try:
            # Build command
            cmd = ["lt", "--port", str(self.local_port)]

            # Add subdomain if provided
            if self.subdomain:
                cmd.extend(["--subdomain", self.subdomain])

            # Start localtunnel process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=False,
                bufsize=1
            )

            # Mark as active
            self.active = True

            # Start processing output
            self._output_thread = threading.Thread(target=self._process_output)
            self._output_thread.daemon = True
            self._output_thread.start()

            # Wait for tunnel to be established
            for _ in range(10):
                if self.public_url:
                    return True
                time.sleep(1)

            # If we get here, the tunnel was not established in time
            if not self.public_url:
                self.error = "Timeout waiting for localtunnel to be established."
                self.stop()
                return False

            return True
        except Exception as e:
            self.error = f"Error starting localtunnel: {e}"
            return False

    def stop(self) -> bool:
        """
        Stop the localtunnel forwarder.

        Returns:
            True if successful, False otherwise
        """
        if self.process:
            self.active = False
            self.process.terminate()
            self.process = None
            self.public_url = None
            return True

        return False

def create_forwarder(
    local_port: int,
    local_host: str = "127.0.0.1",
    forwarder_type: str = "ngrok",
    **kwargs
) -> PortForwarder:
    """
    Create a port forwarder.

    Args:
        local_port: Local port to forward
        local_host: Local host to forward from
        forwarder_type: Type of forwarder to use ('ngrok', 'cloudflare', or 'localtunnel')
        **kwargs: Additional arguments for the forwarder

    Returns:
        Port forwarder instance
    """
    if forwarder_type == "ngrok":
        return NgrokForwarder(local_port, local_host, **kwargs)
    elif forwarder_type == "cloudflare":
        return CloudflareForwarder(local_port, local_host, **kwargs)
    elif forwarder_type == "localtunnel":
        return LocalTunnelForwarder(local_port, local_host, **kwargs)
    else:
        raise ValueError(f"Unknown forwarder type: {forwarder_type}")

def get_local_ip() -> str:
    """
    Get the local IP address.

    Returns:
        Local IP address
    """
    try:
        # Create a socket to determine the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

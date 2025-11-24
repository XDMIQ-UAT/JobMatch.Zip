#!/usr/bin/env python3
"""
GCP CLI Wrapper for Platform Access
Documented technical backdoor feature
"""
import sys
import subprocess
import requests
import json
from typing import Optional


class GCPCLIWrapper:
    """Wrapper for GCP CLI backdoor access."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.endpoint = f"{api_url}/api/gcp-cli"
    
    def check_gcloud_installed(self) -> bool:
        """Check if gcloud CLI is installed."""
        try:
            subprocess.run(
                ["gcloud", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def check_authenticated(self) -> bool:
        """Check if GCP CLI is authenticated."""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list", "--filter=status:ACTIVE"],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    def verify_access(self) -> dict:
        """Verify GCP CLI access."""
        response = requests.get(f"{self.endpoint}/verify")
        response.raise_for_status()
        return response.json()
    
    def get_access_token(self) -> str:
        """Get access token."""
        response = requests.get(f"{self.endpoint}/access-token")
        response.raise_for_status()
        data = response.json()
        return data["access_token"]
    
    def execute_command(self, command: str, parameters: Optional[dict] = None) -> dict:
        """Execute CLI command."""
        token = self.get_access_token()
        
        payload = {"command": command}
        if parameters:
            payload["parameters"] = parameters
        
        response = requests.post(
            f"{self.endpoint}/execute",
            headers={"X-GCP-CLI-Token": token},
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_info(self) -> dict:
        """Get CLI backdoor info."""
        response = requests.get(f"{self.endpoint}/info")
        response.raise_for_status()
        return response.json()


def main():
    """CLI interface."""
    wrapper = GCPCLIWrapper()
    
    if len(sys.argv) < 2:
        print("Usage: python gcp-cli-wrapper.py <command> [parameters]")
        print("\nAvailable commands:")
        print("  verify     - Verify GCP CLI access")
        print("  status     - Platform status")
        print("  health     - Health check")
        print("  metrics    - Platform metrics")
        print("  users      - User statistics")
        print("  assessments - Assessment statistics")
        print("  matches    - Match statistics")
        print("  info       - CLI backdoor information")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Check prerequisites
    if not wrapper.check_gcloud_installed():
        print("Error: gcloud CLI not found")
        print("Install from: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)
    
    if not wrapper.check_authenticated():
        print("Error: GCP CLI not authenticated")
        print("Run: gcloud auth login")
        sys.exit(1)
    
    try:
        if command == "verify":
            result = wrapper.verify_access()
            print(json.dumps(result, indent=2))
        
        elif command == "info":
            result = wrapper.get_info()
            print(json.dumps(result, indent=2))
        
        else:
            result = wrapper.execute_command(command)
            if result.get("success"):
                print(result.get("output", ""))
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                sys.exit(1)
    
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


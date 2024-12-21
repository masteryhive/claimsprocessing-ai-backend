from playwright.sync_api import sync_playwright
import subprocess
import sys

def main():
    # Install browsers using playwright CLI
    subprocess.run(["playwright", "install", "chromium"], check=True)
    # Optional: install system dependencies
    subprocess.run(["playwright", "install-deps", "chromium"], check=True)

if __name__ == "__main__":
    main()
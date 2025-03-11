# Streamlabs Nitro Promo Claimer

This script automates the process of claiming Discord Nitro promo codes through Streamlabs. It handles account login, promo code extraction, and account management. The script is designed to work with multiple accounts and proxies to maximize efficiency.

---

## Features

- **Multi-Account Support**: Process multiple accounts simultaneously using threading.
- **Proxy Support**: Rotate proxies to avoid IP bans and rate limits.
- **Promo Code Extraction**: Automatically extracts 1-month and 3-month Discord Nitro promo codes.
- **Account Management**: Removes used or invalid accounts from the list.
- **Error Handling**: Retries failed attempts and logs errors for debugging.

---

## Prerequisites

Before using this script, ensure you have the following:

1. **Python 3.8 or higher**: Download and install Python from [python.org](https://www.python.org/).
2. **Required Libraries**: Install the necessary Python libraries using `pip`.
3. **Accounts File**: A text file (`accs.txt`) containing Streamlabs accounts in the format `email:password`.
4. **Proxies File**: A text file (`proxies.txt`) containing HTTP/HTTPS proxies in the format `ip:port`.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/payload69/streamlabs-promo-puller.git
   cd streamlabs-nitro-claimer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your accounts to `accs.txt` and proxies to `proxies.txt`.

4. Run the script:
   ```bash
   python main.py
   ```

---

## Credits

- **@notlit69**
- **@switchuwu**
- **CF Bypass Support**


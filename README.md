# Cloudflare Solver & Perplexity.ai Scraper

A Python-based solution for handling Cloudflare's Turnstile captcha and scraping Perplexity.ai content with proxy support.

## Features
- 🔒 Automatic Cloudflare Turnstile captcha solving using multiple methods:
  - Automated GUI interaction
  - 2captcha API integration (as fallback)
- 🌐 Proxy support with authentication
- 🤖 Human-like behavior simulation:
  - Random scrolling
  - Mouse movement simulation
  - Randomized delays
- 📊 Data extraction:
  - Perplexity.ai title extraction
  - CSV export functionality
- 🔄 Automatic Chrome version detection
- 📝 Detailed logging system

## Prerequisites
- Python 3.7 or higher
- Google Chrome browser
- Windows/Linux/MacOS supported
- (Optional) 2captcha API key
- (Optional) Residential proxies

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/cloudflare-solver.git
cd cloudflare-solver
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the script:

```bash
python app.py
``` 

4. Set up your proxy configuration:
   - Create a `proxies.txt` file in the root directory
   - Add your proxies in the format: `host:port::username::password`
   - Example:
     ```
     brd.superproxy.io:22225::user123::pass456
     ```

5. Configure 2captcha:
   - Replace `YOUR_2CAPTCHA_API_KEY` in `app.py` with your actual API key or create .env file and add your API key there.

## Usage
 The script will:
   - Initialize Chrome with proxy support
   - Navigate to Perplexity.ai
   - Handle any Cloudflare challenges
   - Extract titles from the Discover page
   - Save results to `perplexity_titles.csv`




## How It Works

### Captcha Solving Process
1. Primary Method: GUI Automation
   - Uses undetected-chromedriver to bypass detection
   - Automatically clicks captcha checkbox
   - Simulates human-like behavior

2. Fallback Method: 2captcha
   - Activates if GUI automation fails
   - Extracts sitekey and other parameters
   - Submits solution via JavaScript injection

### Proxy Integration
- Supports authenticated proxies
- Creates Chrome extension for proxy authentication
- Handles proxy rotation on failure

### Data Extraction
- Waits for page load after captcha
- Locates and extracts titles using Selenium
- Exports data to CSV format

## File Structure
- `app.py`: Main script with core functionality
- `requirements.txt`: Python dependencies
- `proxies.txt`: Proxy configuration file
- `.gitignore`: Git ignore rules
- `perplexity_titles.csv`: Output file for scraped titles

## Configuration Options

### Proxy Format

host:port::username::password




### Chrome Options
- Window size: 1920x1080
- Headless mode: Disabled (required for captcha)
- System-specific optimizations included

## Troubleshooting

1. Chrome Version Mismatch:
   - The script automatically detects your Chrome version
   - Ensure Chrome is up to date

2. Proxy Issues:
   - Verify proxy format in proxies.txt
   - Check proxy credentials
   - Ensure proxy is active and responsive

3. Captcha Failures:
   - Check internet connection
   - Verify 2captcha API key if using
   - Ensure proxy is not blocked

## Error Handling
- Detailed logging system
- Automatic retry mechanism
- Proxy rotation on failure
- Graceful shutdown on errors


## Limitations
- Requires visible Chrome window for captcha
- May be affected by Cloudflare updates
- Proxy quality affects success rate
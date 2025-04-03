# python-automation-scripts
This repository is a collection of miscellaneous python automation scripts for social media automation: 

## Windows setup

To install Chocolatey, Python, pip3, and Selenium on a Windows machine, follow these steps:

Step 1: Install Chocolatey

Open PowerShell as an administrator.
Search for “PowerShell” in the Windows Start Menu, right-click on it, and select Run as administrator.
In the PowerShell window, run the following command to install Chocolatey:

	Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

When the installation completes, verify Chocolatey is installed by running:

	choco --version

This should display the installed version of Chocolatey.

Step 2: Install Python

With Chocolatey installed, you can install Python by running the following command in PowerShell:

	choco install python --version=3.x.x -y

(Replace 3.x.x with the specific version you wish to install, like 3.9.7. The -y flag accepts all prompts automatically.)

After installation, close and reopen PowerShell or Command Prompt to make sure Python is recognized.
Verify the installation by checking the Python version:

	python --version

Step 3: Install pip (if not installed)

Python installations typically include pip by default. However, to ensure it’s installed, you can upgrade it using:

	python -m ensurepip --upgrade

To verify pip is installed, check its version:

	pip --version

Step 4: Install Selenium with pip

With pip installed, install Selenium by running:

	pip install selenium

Verify Selenium installation by opening a Python interpreter and importing Selenium:

	python -c "import selenium; print(selenium.__version__)"

Step 5: Download WebDriver (ChromeDriver or GeckoDriver)

For Selenium to control browsers, you need a WebDriver. For example, if you are using Chrome, download ChromeDriver; if Firefox, download GeckoDriver.

1.	For Chrome:
	•	Go to the ChromeDriver page and download the version that matches your Chrome browser version.
	•	Extract and place the chromedriver.exe file in a directory that is in your system’s PATH (or specify the path explicitly in your Selenium scripts).

2.	For Firefox:
	•	Go to the GeckoDriver page and download the latest version.
	•	Similarly, extract and place geckodriver.exe in a PATH directory.


## MacOS setup
```
brew install python #install python
python3 -m ensurepip --upgrade #install pip3
pip3 install selenium #install selenium
brew install dos2unix #install dos2unix
```
- Download VS code IDE application https://code.visualstudio.com/download. It's really easy to manage and run the scripts with it on desktop.
- MAKE SURE you disable screen/laptop sleep/off or such energy saving features https://support.apple.com/en-me/guide/mac-help/mchlp1168/mac#:~:text=To%20open%20the%20pane%2C%20choose,may%20need%20to%20scroll%20down.)&text=Prevent%20your%20Mac%20from%20going,when%20its%20display%20is%20off.&text=Even%20in%20sleep%20mode%2C%20wake,shared%20printers%20or%20Music%20playlists. because the scripts will run for long time without user input.
- Create a folder in VS Code Navigation pane where you will store all the input and code files for this application.
- copy python scripts from repository and supporting files into this directory
- open a terminal window

## convertcontacts.py

This script converts outlook csv file into an input file to run sendwhatsapp.py script. It ensures that phone numbers are standardized and that each contact's multiple phone numbers are handled correctly.

### Features

- Formats US phone numbers to start with "+1".
- Handles multiple phone numbers for a single contact.
- Identifies and logs invalid phone numbers.
- Identifies and logs duplicate phone numbers.
- Outputs a clean CSV file with no extra commas or unnecessary whitespace.

### Usage

1. **Prepare your input OUTLOOK CSV file**: Ensure that your CSV file contains the following columns:
   - `First Name`
   - `Primary Phone`
   - `Home Phone`
   - `Home Phone 2`
   - `Mobile Phone`
   - `Business Phone`
   - `Business Phone 2`
   - `Other Phone`

2. **Run the script**: Use the following command to run the script:

   ```
   python outlook_contacts_processor.py input_file.csv output_file.csv [-v]

   input_file.csv: The path to the input CSV file containing Outlook contacts.
   output_file.csv: The path where the processed contacts will be saved.
   -v or --verbose: Optional flag to enable verbose output for debugging.
   
   Example
   python outlook_contacts_processor.py contacts.csv processed_contacts.csv -v
   Output
   
   The script will generate an output CSV file (processed_contacts.csv) with the following columns:
   
   Phone: The formatted phone number.
   Name: The cleaned first name of the contact.
   ```

### Example Input and Output

#### Input CSV (contacts.csv)
   ```
   First Name,Primary Phone,Home Phone,Mobile Phone,Business Phone
   John Doe,(123) 456-7890,,(987) 654-3210,
   Jane Smith,,(555) 555-5555,(444) 444-4444
   Alice Johnson,,,(222) 222-2222,1-800-555-0199
   Bob Brown,(111) 222-3333,,(111) 222-3333,
   ```
#### Output CSV (processed_contacts.csv)
   ```
   Phone,Name
   +11234567890,John
   +19876543210,John
   +15555555555,Jane
   +14444444444,Jane
   +12222222222,Alice
   +18005550199,Alice
   +1112223333,Bob
   ```



## removecontacts.py
This script automates removing contacts from a CSV file based on a list of phone numbers to be excluded.

### Features
- **Automated Removal**: Removes specified phone numbers from the input file.
- **Formatted Exclusion**: Strips spaces and non-numeric characters before processing.
- **Logging**: Displays a summary of processed, removed, and retained contacts.
- **Validation**: Identifies numbers from the exclusion list that were not found in the input file for cross-checking.
- **Cross-Platform**: Compatible with Windows, macOS, and Linux.

### Prerequisites
- Python 3.x

### Usage
Command-line Arguments

- `input_file`: Path to the input CSV file containing phone numbers.
- `remove_file`: Path to the file containing phone numbers to be removed.
- `output_file`: Path to save the processed file after removals.

### Example:
```sh
python removecontacts.py input.csv remove.csv output.csv
```

### Input Files
**input.csv**:
A comma-delimited file with phone numbers and names.
Format: `phone_number, name`
Example:
```
1234567890,John Doe
9876543210,Jane Smith
```

**remove.csv**:
A file containing phone numbers to be removed (one per line).
Format:
```
1234567890
9876543210
```

### Behavior and Logic
1. **Read and Format**: Reads the exclusion list and strips non-numeric characters.
2. **Processing**: Iterates through the input file, removing lines with excluded phone numbers.
3. **Logging**: Prints a summary of records processed, removed, and retained.
4. **Cross-Check**: Displays numbers from the exclusion list that were not found in the input file.

### Troubleshooting
- Ensure that phone numbers in both files are formatted consistently.
- Run the script with administrative privileges if file permissions cause errors.
- If numbers are not removed as expected, check the output for unprocessed exclusion numbers.

### Notes
- The script overwrites the exclusion file with properly formatted phone numbers before processing.
- Use a text editor or spreadsheet tool to inspect input files before running the script.


## sendwhatsapp.py

This script automates sending personalized WhatsApp messages with attachments to multiple contacts using Selenium WebDriver.

### Features

- **Personalized Messaging**: Send customized text messages to multiple WhatsApp contacts.
- **Attachments**: Attach up to 3 images or video files per message.
- **Variable Substitution**: Use variables (x1, x2, x3) in your messages for personalization.
- **CSV Input**: Read contact numbers and variables from a CSV file.
- **Logging**: Keep track of successful sends and errors in separate log files.
- **Cross-Platform**: Compatible with Windows, macOS, and Linux.
- **Configurable Wait Times**: Adjust the wait time for WhatsApp Web to load.

### Prerequisites

- Python 3.x
- Selenium WebDriver
- Chrome browser
- ChromeDriver (ensure it's compatible with your Chrome version)
  
- ==>> DISABLE any laptop energy saving features for shutting off monitor/hard drive with prolonged inactivity. This is because the script will run for long.

### Usage
Command-line Arguments

```
-n, --numbersfile: CSV file containing WhatsApp contact numbers (default: numbers.csv).
-m, --messagefile: Text file containing the message template (default: message.txt).
-a, --attachments: Attachment files to send (images, videos, etc.).
-w, --wait: How long to wait to let the Whatsapp web home load on computer
```

### Input Files
numbers.csv: 

A comma-delimited file with WhatsApp contact numbers and variables.
```
Format: phone_number,var1,var2,var3
Example:
1234567890,John,Engineer,New York
9876543210,Jane,Designer,San Francisco
```

message.txt:

A text file containing the message template with variables x1, x2, x3.
Example:
```
Hello x1,
We're excited to have you as a x2 in x3!
```

Attachment Files:
Image or video files to be sent (optional).
Supported formats: JPEG, PNG, MP4, etc.

### Examples

###### WHATSAPP MESSAGE ######

```
# First export contacts from Google into outlook format
# and Remove special chars 
dos2unix KIcontacts26mar2025.csv

# convert OUTLOOK format file to input file format for sending whatsapp messages
python3 convertcontacts.py KIcontacts26mar2025.csv KIcontacts26mar2025_formatted.csv

# If needed, you can exclude recent contacts who do not need to be contacted 
python3 removecontacts.py KIcontacts26mar2025_formatted.csv exclude.csv KIcontacts26mar2025_formatted_excluded.csv

# now you can send whatsapp message  (and image or videos) for the event with the scrubbed, formatted contact list
# see various examples below

python3 sendwhatsapp.py -n jhulan.csv -m jhulan.txt

python3 sendwhatsapp.py -n KIcontacts26mar2025_formatted_excluded.csv -m kirtanappeal.txt

python3 sendwhatsapp.py -n kc2024.csv -m janmastmi.txt -a janmastmi.jpeg

python3 sendwhatsapp.py -n numbers.csv -m kirtan.txt -a k1.MP4 k2.MP4 k3.MP4

```

### Behavior and Logic
Initialization: Parses arguments and validates input files.
WebDriver Setup: Initializes Chrome WebDriver with a custom user data directory.
WhatsApp Web Loading: Loads WhatsApp Web and waits for -wait X minutes argument value for full Whatsapp web home page load only for the first time.

### Message Sending Process:
For each contact in the CSV file:
Navigates to the WhatsApp chat for that number.
Personalizes the message using variables from the CSV.
Sends the personalized message.
Sends attachments one by one (if provided).
Adds a random delay (5-10 seconds) between actions.
Logging: Logs successful sends in a .sent file and errors in a .err file.

### Notes
Ensure WhatsApp Web is properly set up in your Chrome browser.
You would need to scan the QR code on the first run or if the session expires.

### Troubleshooting
If the Whatsapp home page load hangs after -wait X minutes argument value minutes:
Re-run the script
Click LOGOFF on the Chrome window
Scan the QR code again

To clear the WhatsApp cache:
```
Unix/Linux: rm -rf /tmp/whatsapp
Windows: Delete the contents of %USERPROFILE%\AppData\Local\Google\Chrome\User Data
```

## fbgrouppost.py

### Input files:
- messagefile: A file with main body message for FB group 
- groupsfile: A file with list of FB group URLs. Rows that should not be processed can be commented with # at the beginning
- profilefile: A file with URL of the profile from where you want to post
  

### usage examples:
```
python3 fbgrouppost.py -h
python3 fbpostnew.py --username <username> --password <pwd> --message_file <msgfile> --groups_file <groupsURLsfile> --profile_url_file=<profilefile>
```

## getfbgroups.py

This Python script is designed to automate the process of collecting Facebook group links. It uses Selenium WebDriver to interact with the Facebook website, log in to a user account, and scrape links to groups the user has joined.

### Key Features

1. **Automated Login**: The script logs into Facebook using provided credentials.
2. **Profile Switching**: It can optionally switch to a specified Facebook profile after login.
3. **Group Link Collection**: The script navigates to the user's joined groups page and collects unique group links.
4. **Scrolling Mechanism**: It implements an infinite scroll to load all group links on the page.
5. **Link Cleaning**: The collected links are cleaned to remove unnecessary parameters.
6. **Logging**: Comprehensive logging is implemented for debugging and tracking the script's progress.
7. **Error Handling**: The script includes try-except blocks to handle potential exceptions.

### Main Components

1. **Selenium Setup**: Uses Chrome WebDriver with custom options to disable notifications.
2. **Login Function**: Handles the Facebook login process, including cookie acceptance if needed.
3. **Profile Switching Function**: Allows switching to a specific Facebook profile if required.
4. **Link Collection Function**: Scrolls through the joined groups page and collects unique group links.
5. **Argument Parsing**: Uses argparse to handle command-line arguments for username, password, and optional profile URL.

### Usage

The script is run from the command line with the following arguments:
- `--username`: Facebook username or email (required)
- `--password`: Facebook password (required)
- `--profileurl`: URL of the profile to switch to (optional)

### Output

The collected group links are saved to a file named `facebook_groups.txt`, with one link per line.

### Notes

- The script uses time delays to allow for page loading, which may need adjustment based on internet speed and Facebook's response time.
- It's designed to handle cookie acceptance prompts and profile switching, making it versatile for different Facebook account setups.
- The link collection process filters out non-group links and removes unnecessary URL parameters for cleaner results.

This script can be particularly useful for users who need to collect links to their joined Facebook groups for various purposes, such as community management or data analysis.

## redditpost.py

### Input files:
- titlefile: A file with the title of the message to be posted
- messagefile: A file with main body message for the reddit post 
- groupsfile: A file with list of Reddit group URLs. Rows that should not be processed can be commented with # at the beginning
- chromedriver: The chromedriver file for MacOS/unix

### usage examples:
```
python3 redditpost.py -h
python3 redditpost.py -u <Reddituser> -p <Redditpassword> -t titlefile -m messagefile -g groupsfile -d chromedriver 
```

## youtubepost.py

### Input files:
- keywordsfile: A file with search keywords for youtube videos on which comments will be posted
- commentsfile: A file with a list of comments (one per line). Only one comment is randomly chosen from the list
- videosfile: A filename where a list of videos will be generated for the keywords specificed in keywordsfile
- overwritevideosfileflag: Yes/Y tells the program to create the videosfile fresh otherwise it uses the preexisting list of videos
- nofscrolls: a number specifying how many pages worth of search results need to be captured in videosfile
- chromedriver: The chromedriver file for MacOS/unix

### usage examples:
```
python3 youtubepost.py -h
python3 youtubepost.py -k keywordsfile -c commentsfile -v videosfile -o overwritevideosfileflag -s nofscrolls -d chromedriver 
```
## sendlinkedinDMs.py

This Python script is designed to automate the process of sending personalized CONNECTION messages to LinkedIn profiles. It uses Selenium WebDriver to interact with the LinkedIn website, log in to a user account, and send messages to specified profiles.

### Key Features
- Automated Login: The script logs into LinkedIn using provided credentials.
- Message Personalization: It includes the recipient's name in the message for a personalized touch.
- Attachment Support: The script can optionally attach a file to the message.
- Error Handling: Comprehensive logging and error handling are implemented for debugging and tracking the script's progress.
- Input File Support: The script reads profiles and messages from input files for easy management.

### Main Components
- Selenium Setup: Uses Chrome WebDriver with custom options to disable notifications.
- Login Function: Handles the LinkedIn login process.
- Message Sending Function: Sends personalized messages to specified profiles with optional attachments.
- Argument Parsing: Uses argparse to handle command-line arguments for username, password, input file, message file, and optional attachment file.

### Usage
The script is run from the command line with the following arguments:

--username: LinkedIn username or email (required)

--password: LinkedIn password (required)

--inputfile: Path to the input file containing list of names and profile URLs in comma separated format (required)

--messagefile: Path to the input file containing the message (required)

--attachmentfile: Path to the attachment file (optional) # not working yet

```
python3 sendlinkedinmessage.py --username [username] --password [pwd] --inputfile [file with list of names, linkedin profiles] --messagefile [message file]
```

## sendlinkedinconnections.py

The script `sendlinkedinconnections.py` is designed to automate the process of sending personalized messages to LinkedIn profiles. You can specify the message template, the search results url, and the # of pages of connections to be contacted. It uses Selenium WebDriver to interact with the LinkedIn website, log in to a user account, and send messages to specified profiles. There is a 30 sec delay on the login page to handle the visual human challenge if needed.

### Key Features
- **Automated Login**: The script logs into LinkedIn using provided credentials.
- **Message Personalization**: It includes the recipient's name in the message for a personalized touch.
- **Error Handling**: Comprehensive logging and error handling are implemented for debugging and tracking the script's progress.
- **Input File Support**: The script reads the search results url from input files for easy management.

### Main Components
- **Selenium Setup**: Uses Chrome WebDriver with custom options to disable notifications.
- **Login Function**: Handles the LinkedIn login process.
- **Message Sending Function**: Sends personalized messages to specified profiles.
- **Argument Parsing**: Uses argparse to handle command-line arguments for username, password, input file, message file, and optional search URL file.

### Usage
The script is run from the command line with the following arguments:

--username: LinkedIn username or email (required)

--password: LinkedIn password (required)

--messagefile: Path to the file containing the message template (required)

--pages: Number of search result pages to process (default: 1)

--searchurlfile: Path to the file containing the search results URL (required)

```python
python3 sendlinkedinconnections.py --username [username] --password [pwd] --messagefile [message file] --pages 1 --searchurlfile [search URL file]
```

### Flow
1. **Setup**: The script initializes the Chrome WebDriver with custom options.
2. **Login**: It logs into LinkedIn using the provided credentials.
3. **Get Profile Links**: The script retrieves profile links from the search results URL.
4. **Visit Profiles**: It visits each profile, extracts the first name, and sends a personalized message.
5. **Error Handling**: The script logs any errors that occur during the process.

## followlinkedincontacts.py

The script `followlinkedincontacts.py` is designed to automate the process of FOLLOWING LinkedIn profiles. You can specify the search results url, and the # of pages of connections to be contacted. There is a 30 sec delay on the login page to handle the visual human challenge if needed. This script is especially useful if you have hit your 100 connection requests per week limit with Linkedin. You can still follow people and engage with their posts, increasing chances of them accepting your connection request later.

### Key Features
- **Automated Login**: The script logs into LinkedIn using provided credentials.
- **Error Handling**: Comprehensive logging and error handling are implemented for debugging and tracking the script's progress.
- **Input File Support**: The script reads search results url from input files for easy management.

### Main Components
- **Selenium Setup**: Uses Chrome WebDriver with custom options to disable notifications.
- **Login Function**: Handles the LinkedIn login process.
- **Message Sending Function**: Sends personalized messages to specified profiles.
- **Argument Parsing**: Uses argparse to handle command-line arguments for username, password, input file, message file, and optional search URL file.

### Usage
The script is run from the command line with the following arguments:

--username: LinkedIn username or email (required)

--password: LinkedIn password (required)

--searchurlfile: Path to the file containing the search results URL (required)

--pages: Number of search result pages to process (default: 1)

```python
python3 sendlinkedinconnections.py --username [username] --password [pwd]  --pages 1 --searchurlfile [search URL file]
```

### Flow
1. **Setup**: The script initializes the Chrome WebDriver with custom options.
2. **Login**: It logs into LinkedIn using the provided credentials.
3. **Get Profile Links**: The script retrieves profile links from the search results URL.
4. **Visit Profiles**: It visits each profile, follows contact.
5. **Error Handling**: The script logs any errors that occur during the process.

## sendfreelinkedinmessages.py

The script `sendfreelinkedinmessages.py` sends free linkedin messages for the profiles that have open profiles. You can specify mutliple search results urls, and the # of pages of connections to be contacted per search results url. There is a 30 sec delay on the login page to handle the visual human challenge if needed. This script is especially useful if you have hit your 100 connection + following requests per week limit with Linkedin. 

### Key Features
- **Automated Login**: The script logs into LinkedIn using provided credentials.
- **Error Handling**: Comprehensive logging and error handling are implemented for debugging and tracking the script's progress.
- **Input File Support**: The script reads multiple search results url from input files for easy management.
- **Message file Support**: The script reads the subject line and body from the message file

### Main Components
- **Selenium Setup**: Uses Chrome WebDriver with custom options to disable notifications.
- **Login Function**: Handles the LinkedIn login process.
- **Message Sending Function**: Sends personalized messages to specified profiles.
- **Argument Parsing**: Uses argparse to handle command-line arguments for username, password, input file, message file, and optional search URL file.

### Usage
The script is run from the command line with the following arguments:

--username: LinkedIn username or email (required)

--password: LinkedIn password (required)

--searchurlfile: Path to the file containing the search results URL (required)

--pages: Number of search result pages to process (default: 1)

```python
python3 sendlinkedinconnections.py --username [username] --password [pwd]  --pages 1 --searchurlfile [search URL file] --messagefile [message file]
```

### Flow
1. **Setup**: The script initializes the Chrome WebDriver with custom options.
2. **Login**: It logs into LinkedIn using the provided credentials.
3. **Get Profile Links**: The script retrieves profile links from the search results URL.
4. **Visit Profiles**: It visits each profile, sends free message to contact if qualified.
5. **Error Handling**: The script logs any errors that occur during the process.




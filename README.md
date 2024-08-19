# python-automation-scripts
This repository is a collection of miscellaneous python automation scripts for social media automation: 

## MacOS setup
```
brew install python #install python
python3 -m ensurepip --upgrade #install pip3
pip3 install selenium #install selenium
brew install dos2unix #install dos2unix
```
- Download VS code IDE application. It's really easy to manage and run the scripts with it on desktop.
- MAKE SURE you disable screen/laptop sleep/off or such energy saving features because the scripts will run for long time without user input.
- Create a folder where you will store all the input and code files for this application.
- copy python and awk scripts from repository into this directory

## convertcontacts.py

This script converts outlook csv file into an input file to run sendwatextimage.py script. It ensures that phone numbers are standardized and that each contact's multiple phone numbers are handled correctly.

### Features

- Formats US phone numbers to start with "+1".
- Handles multiple phone numbers for a single contact.
- Identifies and logs invalid phone numbers.
- Identifies and logs duplicate phone numbers.
- Outputs a clean CSV file with no extra commas or unnecessary whitespace.

### Usage

1. **Prepare your input CSV file**: Ensure that your CSV file contains the following columns:
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

### Usage
Command-line Arguments

```
-n, --numbersfile: CSV file containing WhatsApp contact numbers (default: numbers.csv).
-m, --messagefile: Text file containing the message template (default: message.txt).
-a, --attachments: Attachment files to send (images, videos, etc.).
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
Attachment Files:
```

Image or video files to be sent (optional).
Supported formats: JPEG, PNG, MP4, etc.

### Examples

```
python sendwhatsapp.py -h
python sendwhatsapp.py -n contacts.csv -a image1.jpeg image2.jpeg
python sendwhatsapp.py -n leads.csv -a product_video.mp4 -m sales_pitch.txt
```

### Behavior and Logic
Initialization: Parses arguments and validates input files.
WebDriver Setup: Initializes Chrome WebDriver with a custom user data directory.
WhatsApp Web Loading: Loads WhatsApp Web and waits for 3 minutes for full page load.

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
You may need to scan the QR code on the first run or if the session expires.
The script waits for 3 minutes for the initial WhatsApp Web page load. Adjust this in the code if needed.
Troubleshooting
If the page load hangs after 5 minutes:
Re-run the script
Click LOGOFF on the Chrome window
Scan the QR code again
To clear the WhatsApp cache:
Unix/Linux: rm -rf /tmp/whatsapp
Windows: Delete the contents of %USERPROFILE%\AppData\Local\Google\Chrome\User Data

## fbgrouppost.py

### Input files:
- messagefile: A file with main body message for FB group 
- groupsfile: A file with list of FB group URLs. Rows that should not be processed can be commented with # at the beginning
- profilefile: A file with URL of the profile from where you want to post
- 

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

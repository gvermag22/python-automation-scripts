# python-automation-scripts
This repository is a collection of misc python automation scripts for utility. It covers whatsapp personalized message sending etc.

## Requirements:
- Numbers.csv - Comma delimited file with Whatsapp contact# and variables.
- Message.txt - A file with text message and variables x1, x2, x3 where ever you want to switch the variables like 
- image[1-3].jpeg - Upto 3 image files to be sent to whatsapp contacts
- 
## MacOS
- Install python by opening terminal and typing <code>brew install python </code>.
- Once python is installed, install selenium <code>pip install selenium </code> or <code> pip3 install selenium </code> 
- install pip with <code>brew install pip3</code>) if you don't have it already.
- Create a folder where you will store all the files for this application.
- Get a copy of <code> send.py </code> and keep it in the folder that you made.
- Go to [chromedriver](https://chromedriver.chromium.org/downloads) and download the chrome driver according to your chrome version and OS. Extract The file in the same folder as the code.
- create files with contacts and the messages in the same folder as web driver.
- Once you have your contacts files and the message file in the computer, go to the terminal and type the following code:
- 
- <code> cd path/of/the/directory/with/code </code>.
- <code> python3 sendtext.py -h </code> or
- <code> python3 sendimage.py -h </code> or
- 
-
- If you get an error saying '“chromedriver” can’t be opened because Apple cannot check it for malicious software' just run the follwing command:<code>xattr -d com.apple.quarantine chromedriver</code>

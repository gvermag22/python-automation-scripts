# python-automation-scripts
This repository is a collection of miscellaneous python automation scripts for social media automation: 

- sendtext.py and sendimage.py are for sending personalized Whatsapp text and image messages
- redditpost.py is for posting personalized messages on reddit groups
- fbgrouppost.py is for posting messages on facebook groups
- youtubepost.py is for posting comments to top videos that are returned for specified keywords

Right now, these run well on Unix or MacOS.

- As of June 5 2022, these scripts are working fine. 
- However, Whatsapp will keep changing the UI structure and the scripts are expected to break at some point. 
- Mainly, the xpath value of UI/text components will need to be verified/updated.

## MacOS setup
```
brew install python #install python
brew install pip3 #install pip3
pip3 install selenium #install selenium
brew install dos2unix #install dos2unix
```
- download the chrome driver according to your chrome version and OS from https://chromedriver.chromium.org/download
- xattr -d com.apple.quarantine chromedriver

- Create a folder $BASE_FOLDER where you will store all the input and code files for this application.
- copy python and awk scripts from repository into this directory

## Contacts setup
find
cd $BASE_FOLDER

Before running any of the python scripts, you should run these scripts to sanitize and prepare your contacts list:

```
dos2unix numbers.csv # remove special return characters from the csv file to avoid weird errors. This is important. 

awk -f fixcontacts.awk phonepos=2 namesuffix="ji" numbers.csv > numbers2.csv # format the contacts in whatsapp friendly format (+1XXXXXXXXXX) and put a suffix to name if needed (cultural nuance). This assumes numbers.csv will have only two fields. You can extend it as needed for more fields.

findcommon.sh file1.csv file2.csv # Use this to find common whatsapp numbers in file1.csv and file2.csv. This is important to avoid sending conflicting/duplicate messages to your audience
```

## sendtext.py

### Input files:
- numbers.csv: A comma delimited file with Whatsapp contact# and variables. Rows that should not be processed can be commented with # at the beginning of the line
- message.txt: A file with text message and variables x1, x2, x3 where ever you want to switch the variables like 
- chromedriver: The chromedriver file for MacOS/unix

### usage examples:
```
python3 sendtext.py -h # get help on usage
python3 sendtext.py -n numbers.csv -m message.txt -d chromedriver # these argument values are defaulted even if the option is not specified
python3 sendtext.py -n contacts.csv -m message1.txt # send message in message1.txt to contacts in contacts.csv. Note chromedriver file name is defaulted
```

## sendimage.py

### Input files:
- numbers.csv: A comma delimited file with Whatsapp contact# and variables. Rows that should not be processed can be commented with # at the beginning of the line
- message.txt: A file with text message and variables x1, x2, x3 where ever you want to switch the variables like 
- image[1-3].jpeg: The names of upto 3 image files to be sent to whatsapp contacts
- chromedriver: The chromedriver file for MacOS/unix

### usage examples:
```
python3 sendimage.py -h
python3 sendtext.py -n numbers.csv -i image1.jpeg image2.jpeg image3.jpeg -d chromedriver # these argument values are defaulted when option is not specified
python3 sendtext.py -n numbers.csv -i image1.jpeg -m imagemessage.txt -d chromedriver # Send image1.jpeg to contacts in numbers.csv with personalized text in imagemessage.txt. Tokens are taken fom colum 2 onwards in numbers.csv and substituted in imagemessage.txt before sending.
python3 sendtext.py -n numbers.csv -i image1.jpeg image2.jpeg -m imagemessage.txt -d chromedriver # Send image1.jpeg and image2.jpeg to contacts in numbers.csv with personalized text in imagemessage.txt. Tokens are taken fom colum 2 onwards in numbers.csv and substituted in imagemessage.txt before sending. The text is ONLY sent along with image1.jpeg.
```

## fbgrouppost.py

### Input files:
- messagefile: A file with main body message for FB group 
- groupsfile: A file with list of FB group URLs. Rows that should not be processed can be commented with # at the beginning
- chromedriver: The chromedriver file for MacOS/unix

### usage examples:
```
python3 fbgrouppost.py -h
python3 fbgrouppost.py -u <fbuser> -p <fbpassword> -m messagefile -g groupsfile -d chromedriver 
```

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
- titlefile: A file with the title of the message to be posted
- messagefile: A file with main body message for the reddit post 
- groupsfile: A file with list of Reddit group URLs. Rows that should not be processed can be commented with # at the beginning
- chromedriver: The chromedriver file for MacOS/unix

### usage examples:
```
python3 youtubepost.py -h
python3 youtubepost.py -k keywordsfile -c commentsfile -v videosfile -o overwritevideosfileflag -s nofscrolls -d chromedriver 
```
# NTNU-Course-Selenium-Bot
For making my program to receive the same validate code image with the website, I wrote this program using Python selenium (爬蟲) but not Python requests.

This is the only way I found.

## Course taking bot

### Preparation
Before execute the program, you will have to install some requirements.

1. Webdriver

   First of all, you have to download [webdriver of Google Chrome](https://chromedriver.chromium.org/downloads).
   
   Notice, the version of webdriver you download must be the same with your Google Chrome.
   
   You can check your Google Chrome version in "Setting" -> "About Chrome".

2. Python libraries

   Just type the command `pip install -r requirements.txt`.
   
3. Weights file (`.h5` file)

   You can download the weights file at [here](https://drive.google.com/file/d/1qdB1SECI-cwqbUQNbJ834EcRAX07i4Z5/view?usp=sharing).
   
   After download it, don't forget to edit the path in `main.py`.
   
4. Account information (username & password) & ids of courses you wish to take

   Execute the program `main.py` and it will create a file named `account.txt`.
   
   Edit the file and run the program again.
   
### Execution

Just execute the program `main.py`.

### Notice

It's better for you to keep the browser on the top of your desk.

Otherwise, it went wrong sometimes and I'm not sure about the reason.

## Course vacancy monitor

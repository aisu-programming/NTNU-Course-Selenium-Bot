# NTNU-Course-Selenium-Bot
For making my program to receive the same validate code image with the website, I wrote this program using Python selenium (爬蟲) but not Python requests.

This is the only way I found.

## Preparation
Before execute the program, you will have to install some requirements.

1. Webdriver (`chromedriver.exe`)

   First of all, you have to download [webdriver of Google Chrome](https://chromedriver.chromium.org/downloads).
   
   Notice, the version of webdriver you download must be the same with your Google Chrome.
   
   You can check your Google Chrome version in "Setting" -> "About Chrome".

   Please unzip the file and put the `chromedriver.exe` in the directory `chromedriver_win32`.

2. Python libraries

   Just type the command `pip install -r requirements.txt`.
   
3. Weights file (`val_loss.h5`)

   You can download the weights file at [here](https://drive.google.com/file/d/16YL-915VVvY0bSMr2FiKhVnV19ipYF59/view?usp=sharing).
   
   And put it in the directory `weights`.
   
4. Account information (username & password) & information of courses you wish to take

   Execute the program `course-taking-bot.py` or `course-vacancy-monitor.py`, and it will create a file named `account.txt`.
   
   Edit the file and run the program again.
   
## Course taking bot

Just execute the program `course-taking-bot.py`.

## Course vacancy monitor

Just execute the program `course-vacancy-monitor.py`.

For those who want LINE Notifications, you can change the variable `LINE_NOTIFY_BOT` into `True`.

And copy the AccessToken of your LINE Notify Bot into the file `LineNotifyBot_AccessToken.txt`.

## Notice

It's better for you to keep the browser on the top of your desk.

Otherwise, it went wrong sometimes and I'm not sure about the reason. Maybe it's an issue about rendering.

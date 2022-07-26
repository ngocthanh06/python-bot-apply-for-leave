# Bot Python

[![Watch the video](https://i.imgur.com/vKb2F1B.png)](https://user-images.githubusercontent.com/33601978/180923775-92c87ce3-87fd-4a85-950c-bc0f478530d0.mov)

## Installation

```
cp .exam.env .env
```
## Update key in .env

# Install package
```
pip install slack_sdk
pip install python-dotenv
pip install gspread
```

```
export FLASK_APP=app_slack
flask run #default port: 5000
```
## Install ngrok

```
pip install ngrok
ngrok http 5000
```

## Update key google clound in folder config

#Deploy heroku

```
heroku ps:scale web=1
python3 -m venv --upgrade-deps venv
source venv/bin/activate #install package 
# or
pip freeze > requirements.txt
```

and push heroku
```
git commit -am 'comment'
git push heroku master
```

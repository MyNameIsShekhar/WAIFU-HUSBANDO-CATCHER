# Pyrogram-Heroku Bot
A Simple Example explaining how to host pyrogram-made bots in Heroku.

## Getting Started
#### 1. Obtain a Bot Token from @botfather in Telegram.
#### 2. [Login](https://id.heroku.com/login) / [Create](https://signup.heroku.com/t/platform?c=7013A000000ib1xQAA&gclid=CjwKCAjw6qqDBhB-EiwACBs6x-E12QzmyEndOYT-7ikg9IdMqyE2YvdpFEvcnOsBD7ugTMdzSUFSABoCzroQAvD_BwE) a Heroku Account.
#### 3. Install [heroku-CLI](https://devcenter.heroku.com/articles/heroku-cli).
#### 4. Install [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
#### 4. Make your own Procfile and requirements.txt as in the Repo above.


## Hosting pyrogram-bot using heroku-CLI:
#### 1. Firstly, go the directory where your bot files are present.
#### 2. Open a Terminal in that directory and login to your account by using the following code.

```$ heroku login```
#### 3. Then create a new app in heroku by executing the following code.

```$ heroku create```

This will assign a random name with git url for your app. To create an app with custom name, execute the following code.

```$ heroku create YourAppName```

#### 4. Now, without asking anything, type the following lines of code one by one.

```
$ git init
$ git add .
$ git commit -m "initial commit"
$ heroku git:remote -a YourAppName
$ git push heroku master
```

You should then see the following messages:

![](https://cdn-images-1.medium.com/max/1000/1*y3JH7a7mY4oYFaAjDCA1Ow.png)

#### 5. Wohooo! you have deployed your bot to heroku.
#### 6. Now, to start the bot, type the following code.

```$ heroku ps:scale worker=1```

#### 7. Now, you would've noticed that the bot starts to respond to your messages.


## Please start and fork my repo if you like it..

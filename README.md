# Cropsiss: Cross Platform Simultaneously Selling System

***Cropsiss*** is a command-line-tool to sell items simultaneously over selling platforms.

The supported platforms are as follows.

- Mercari
- Yahoo!Auction


You can manage your selling items on a Google Spreadsheet.
If your item is sold, the platform sends an email to your Google account.
***Cropsiss*** detects the email to cancel selling of the item on the other platforms, when the item is on the Google Spreadsheet.


The supported languages are as follows.

- Japanese


## Requirements

- Python 3.10 or above
- Google Account
- Google Chrome / Chromium


## Installation

```shell
$ pip install cropsiss
```

## Usage

### Prepare a Google Spreadsheet

Prepare the ID of a Google Spreadsheet to manage your selling items on it.


### Configure the application

You can create a new config file by running:
```shell
$ cropsiss config new
Google Spreadsheet ID(required):  # The Google Spreadsheet ID to manage your selling items
# The others are optional
```

### Login

You can authorize the application for your Google account by running:
```shell
$ cropsiss login
```

### Initialize the Google Spreadsheet

```shell
$ cropsiss sheet init
Initialized the Google Spreadsheet
$ cropsiss sheet open  # Open the Spreadsheet
```

Enter the IDs assigned by the selling platforms to the Spreadsheet.
***Cropsiss*** treats IDs in a row as those of the same selling item.

### Login platform on the browser

You can open the browser for the application by running:
```shell
$ cropsiss browser
```
On the browser, you can login the selling platforms to save your login status.


### Make sure Cropsiss can execute the cancellations

We recommend you make sure ***Cropsiss*** can execute the cancellations.

#### For Mercari
You can suspend the item whose ID assigned by Mercari is `mXXXXXXXXXX` by running:
```shell
$ cropsiss cancel mercari mXXXXXXXXXX
```

#### For Yahoo!Auction
You can cancel the item whose Auction ID assigned by Yahoo!Auction is `XXXXXXXXXX` by running:
```shell
$ cropsiss cancel yahuoku XXXXXXXXX
```

If you want to launch Google Chrome in headless mode, add `--headless` option like this:
```shell
$ cropsiss cancel mercari --chrome-args "--headless" mXXXXXXXXXX
```


### Automate the cancellations

`cropsiss cancel mail` is a command that executes cancellations with the informatioin on the Google Spreadsheet and Gmail messages.

The platforms where you are selling items sends you an e-mail to notify that your item has been sold.
***Cropsiss*** reads the message to cancel selling the same item on the other platforms determined by the information on the Google Spreadsheet.

If you run the command regularly by `cron` on your machine, you can sell an item simultaneously over platforms.

The recommended command is:
```shell
$ cropsiss cancel mail --mail-to foo@example.com --chrome-args "--headless"
```

### Commands

- browser - Open a browser for the application
- cancel -  Cancel selling on a platform
- config -  Configure the application
- login  -  Get a new credentials for Google API
- logout -  Delete the current credentials for Google API
- sheet  -  Manage the Google Spreadsheet


## Docker Image

https://hub.docker.com/repository/docker/huisint/cropsiss

You can build the image from docker file by running:
```shell
$ docker build docker
```

### Sustainability of the system
This system is aimed to connect several services independent of each other.
It means the system will be destroyed if just one of them changes their specification a little. 

- The mail appearance is changed by the platform
- The web page of the platform is changed
- Goolge Chrome version does not match chromedriver version
- Login information on the browser is invalidated


## License

MIT License


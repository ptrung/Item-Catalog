# Item Catalog Project
This projects is a RESTful web application using the Python framework Flask to provide a list of items within a variety of categories. The implemented user registration and authentication system (third-party OAuth authentication Google) enables registered users to post, edit and delete their own items.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Install

First of all, you have to install the following programms: 
1. [Python3](https://www.python.org/downloads)
2. [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
3. [Vagrant](https://www.vagrantup.com/downloads.html)

### Setup the project
1. Download/Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
3. Download/Clone this repository and copy it into Vagrant sub-directory in the *fullstack-nanodegree-vm* 

### Launching the Virtual Machine:
  1. Use your terminal and change the directory to the Vagrant sub-directory and use command `vagrant up` to set up vagrant
  2. Use `vagrant ssh` to log into Vagrant VM

### Run
1. Navigate to the Vagrant directory: `cd /vagrant`
2. Setup the databse: `python database_setup.py`
2. Fill up the database with data: `python dummy_data.py`
3. Run the program with: `python application.py`
4. Open http://localhost:8000/ in your browser to watch the page. 

## JSON Endpoint
You can use the following JSON Endpoints

`/catalog.json` - Data of the whole catalog with categories and items. 

`/categories.json` - Data of all categories

`/catalog/<path:category_name>.json` - Data of the items of a specific category

`/catalog/<path:category_name>/<path:item_title>.json` - Data of a specific item

## Acknowledge

This project was built as part of the Udacity course "Fullstack Web Developer Nanodegree". 
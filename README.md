This app allow every users to share a catalog, users can create/update/delete items and login via facebook third party auth

#Structure:
	* Configuration instructions
	* Operating instructions
	* File manifest
	* Changelog



##Installation instructions
	Before testing this app you have to make sure:
	1. python is installled
	2. flask is installed
	3. copy the github repository via the command line "git clone https://github.com/quentinbt/catalog.git"

##Operating instructions
	1. type the command line "python database_setup.py"
	2. type the command line "python application.py"
	3. open you web browser to "localhost:8000"

##File manifest
	catalog/
	├── static/
	│    └── bootstrap files
	├── templates/
	│    └── html templates
	├── application.py
	├── database_setup.py
	├── fb_client_secrets.json
	├── catalog.db
	└── README.txt

##Changelog
	Check the commit history
This app allow every users to share a catalog, users can create/update/delete items and login via facebook third party auth

#Structure:
	* Configuration instructions
	* Operating instructions
	* Endpoint API
	* File manifest
	* Changelog



##Installation instructions
	Before testing this app you have to make sure:
	1. python is installled
	2. flask is installed
	3. copy the github repository via the command line "git clone https://github.com/quentinbt/catalog.git"
	4. add your fb client id/secret to the fb_client_secrets.json file
	5. add your fb client id in /templates/login.html

##Operating instructions
	1. type the command line "python database_setup.py"
	2. type the command line "python application.py"
	3. open you web browser to "localhost:8000"
	
##Endpoint API
	The app allow JSON endpoint API.
	You can access to this via url:
		http://localhost:8000/catalog/categories/JSON
		http://localhost:8000/catalog/items/JSON
		

##File manifest
	catalog/
	├── static/
	│    └── bootstrap files
	├── templates/
	│    └── html templates
	├── application.py
	├── database_setup.py
	├── fb_client_secrets.json
	└── README.txt

##Changelog
	Check the commit history
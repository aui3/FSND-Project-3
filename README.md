FSND- Project 3 Bookmarks Catalog App
=============

<b>Steps to set up the developement enviroment</b>



1. Follow instructions <a href="https://www.udacity.com/wiki/ud088/vagrant">here </a> to install the virtual machine required to run this project. This virtual machine is configured using vagrant and provides the necessary environment setup to run the project.


2. Please make sure that you follow the instructions under "Run the virtual machine". At the command prompt run the following command

	a) <b>vagrant up</b>

	b) <b>vagrant ssh</b>

	c) <b>cd \vagrant</b>
 

2. You should now be connected to your vagrant machine and inside the folder <b>\vagrant</b>. Change directory to 'tournament' by 

	d) <b>cd \bookmarks</b>



3. Copy all source files from the project here. 



4. Set up the data base to for the project by connecting to psql. At the command prompt type:

	e) <b>psql</b> 



5. To set up the database and views at the command prompt run

	f) <b>python database_setup.py</b>


6. Populate the database with some entries:
	g) <b>python lotsofbookmarks.py</b>


7. Install <b>cloudinary</b> [Using Cloudinary's image services to take a screen shot of the bookmark site. The image url is saved in the database while the image itself is hosted with Coudinary]
	h) <b>sudo pip install cloudinart</b>

8. Install <b>beautifulsoup</b> [Using this python library to extract the title of a webpage that has to be added as a bookmark. The library parses through the html of a given webpage]
	i) <b>sudo pip install beautifulsoup</b>
	

9. Run the project
	j) <b> python project.py</b>


8. To view the project, open the broswer at 

	g) <b>http://localhost:5000</b>





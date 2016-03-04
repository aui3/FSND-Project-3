FSND- Project 3 Bookmarks Catalog App
=============
<b>[Heroku version](http://bookmarks-library.herokuapp.com) </b>

<b>Steps to set up the developement enviroment</b>



1. Follow instructions <a href="https://www.udacity.com/wiki/ud088/vagrant">here </a> to install the virtual machine required to run this project. This virtual machine is configured using vagrant and provides the necessary environment setup to run the project.


2. Please make sure that you follow the instructions under "Run the virtual machine". At the command prompt run the following command

	a) <b>vagrant up</b>

	b) <b>vagrant ssh</b>

	c) <b>cd \vagrant</b>
 

2. You should now be connected to your vagrant machine and inside the folder <b>\vagrant</b>. Change directory to 'tournament' by 

	d) <b>cd \bookmarks</b>


3. Copy all source files from the project here. 


4. To set up the database and views at the command prompt run

	f) <b>python database_setup.py</b>


5. Populate the database with some entries:
	g) <b>python lotsofbookmarks.py</b>

<b>Requirements</b>

	6. Install dependencies using instructions found in requirements.txt
	

7. Run the project

	i) <b> python project.py</b>


8. To view the project, open the broswer at 

	j) <b>http://localhost:5000</b>


9. Quit by pressing Ctrl + C 



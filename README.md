### P4: JSON+SQL--Open Street Map
**Submission report: English**
**Keywords: open street map, london, data cleaning, bad-formatted data**
Pick a city and download its JSON map data from Open Street Map. Clean the data and explore the city virtually.
- Pick London (mainly soho area) and download the map.
- Data cleaning
	- bad street names
	- bad phone numbers
	- bad key names
	- missing values
- Data overview
	- data size
	- contributed users
	- number of theaters
	- ...
- Queries using SQL


### Content
- Data analysis on London OSM.pdf
A pdf document containing answers to the rubric questions. 


- map.txt 
A text file containing a link to the map position of the project, a short description of the area and a reason for the choice. I chose the city of London for the project.

- reference.txt
A text file containing a list of Web sites, books, forums, blog posts, github repositories etc I referred to. Actually the ref list should be much longer than this, but I could not trace them back. Will log them more carefully in the future.

- soho_london.osm
A sample of the map. This area is mainly of (Soho) West End of London, 
where boasts many of the city's major tourist attractions, shops, businesses, government buildings and entertainment venues. 

- osm_schema.py
Python code used for validation in data cleaning.

- data_cleaning.py
Python code used in auditing and cleaning the dataset to get five CSV files ready to be writeen into a SQL database.

- basic_queries.py
Python code used for some basic queries such as how many tags are there, and how many individual users listed in the file.

- sqlquery.py
SQL queries I used to find the answers that I'm interested in the map.

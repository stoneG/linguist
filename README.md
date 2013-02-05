Linguist
========
A web application for testing your linguist-fu.

Type a word into the search bar and get the definition of the word, and a word rarity score. Please note that:

* Scores are only given to players that are logged in.
* Words must be at least 5 characters long (I added this restriction to get rid of words such as AAH AAL AAS ABA ABO).

The pool of possible words is extracted from the [Official Word
List](http://en.wikipedia.org/wiki/Official_Tournament_and_Club_Word_List)
for US Scrabble. Word rarity is calculated from word frequency from [TV & Movie scripts from 2006](http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists#TV_and_movie_scripts). Definitions are provided through the [wordnik.com](http://www.wordnik.com) API.

Check it out [here](http://ec2-107-22-21-172.compute-1.amazonaws.com:13373/)  
Please make an account or use the test account `username/password`: `linguist/linguist`

Under the hood
--------------
* Flask, Psycopg2
* JQuery
* PostGreSQL
* Running on an Amazon EC2 instance

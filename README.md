# BP-Debating-ELO
Calculate ELO rankings of debaters. Currently supports tabs from Tabbie and TabbyCat. I think Tournaman can also output a csv of draws for each round, if so it would be easy to add support for Tournaman also. 

Installation Guide
------------------

### Windows

1. Install Python. Go to the [downloads page](https://www.python.org/downloads/release/python-370/) and download any of the installers -  the instructions should be pretty clear from there.
2. Download and install Git. Similar to the last step, just click download on [this page](https://gitforwindows.org/) and follow any further instruction.
3. Open the windows PowerShell and do the following commands (i.e. type/copy and paste it and press enter):
⋅⋅* `cd documents`
⋅⋅* `mkdir BP-Debating-ELO`
⋅⋅* `cd BP-Debating-ELO`
⋅⋅* `git clone https://github.com/eoin-og/BP-Debating-ELO.git`
⋅⋅* `cd BP-Debating-ELO`
⋅⋅* `pip install -r requirements.txt`


Running the Program
-------------------
1. Go the file **tab_urls.txt** in the folder **input_data**. This is a text file which contains a list of tab urls, separated by new lines. By default this contains the tabs for the Trinity Open 2018, Earlsfort Open 2018, and the GUU Summer Cup 2018. Simply add any Tabbie/Tabbycat urls to this file to calculate the elo rankings after those competitions. The list should be in chronological order as that is the order in which the files will be processed.
2. If you are using any Tabbie tabs you will need to edit the file **tabbie_login.txt** in the folder **input_data**. Change the words email and password to your own. Your log in details are needed to access team records (e.g. https://www.tabbie.org/guu-summer-cup-/team/28124, you can't see that page unless you are logged into tabbie). Your username and password are not saved by the program.
3. Open the windows PowerShell and do the following commands:
..* `cd documents/BP-Debating-ELO/BP-Debating-ELO`
..* `python main.py`
This will run the program and calculate the elo rankings. At this point it should be pretty clear if any error has occurred.
4. To see results go to the folder **output_data**. In this there will be three folders:
..* **elo**: This folder contains the file **master_elo.csv**. This contains the elo score for all speakers, overall and after each competition. Csv files can be opened in excel/google sheets. This folder also contain files which show each teams elo changes over the course of a competition.
..* **speaker**: This folder contains csv files with a list of speakers and associated team names for each competition. If you notice in the final elo rankings a speaker has appeared twice because of different name spellings (e.g. ronan, ronán) change these files so that their name is consistent -  then run the program again.
..* **results**: Csv files for each tourament detailing the result for each room in the competition. Not much interesting here.

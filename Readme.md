# Overview
This is an API tool to obtain statistics from the mobile game Clash of Clans. The initial commit has just a few of the API functionality available, but may be expanded upon later. 

COC documentation: https://developer.clashofclans.com/#/

# Usage
Download or clone this repository. There are two python scripts:

* cocapi.py - this is the primary API request module containing the functionality to send and receive requests
* coc_stats.py - this is a program which imports the cocapi module, obtains CWL stats, and then produces an Excel file for further analysis

In the same folder as these python files, save a file called api_token.json. This should contain a dictionary of the form:

~~~~
{
"token": "string_text_of_api_token_from_developer_site"
,
"clan_tag": "#AA11BB22"
}
~~~~

To obtain an API token, navigate to the developer site, create an account, go to My Account, then create a key. You will need your IP address which can be obtained from https://www.whatismyip.com/.

From there, run the coc_stats.py file and the output will be an Excel file with CWL stats if available.
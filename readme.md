# WebLink - Webring Manager
A simple script for managing a web ring in a peer-to-peer fashion. 

This is a very early version of the script and lots of work still needs to be done.

## Setup
Clone the repository and run the script to configure a node

> Setting a masternode URL will retrieve an initial site list from the host making it easy for anyone to join the webring and retrieve a current list of members. 

Copy the webring.json file to your webserver at the path designated during node configuration

> You will be asked to configure a path for the location of `webring.json`. Omitting a path will assume `webring.json` is located at the root of the webserver

Have a member of the webring add you as a peer for your list to sync with other webring members


## Usage
`python webring.py` - Will initialize the webring and allow you to configure a node. If a node is already configured it will simply dump the contents of `webring.json`

### Commands
`addpeer` - Adds a node to the site list (peers will need to be manually synced after addition at this time)

`syncpeer [url (optional)]` - Syncs data with all nodes in the sites list. Specifying the url path of a node where `webring.json` is located will sync site data for that specific node.

`addsite` - Create an entry in the sites list for a website that is not configured as a WebLink node

## Example JSON Data

```json
{
    "node": 
      {
        "title": "example",
        "url": "example.com",
        "ring_url": "example.com",
        "avatarb64": "garble==",
        "gpg": "public_key",
        "master_node_url": "",
        "blacklist": []
      },
    "sites": [
      {
        "title": "example",
        "url": "example.com",
        "ring_url": "example.com",
        "avatarb64": "garble==",
        "gpg": "public_key"
      }
    ]
  }
```

## To Do
- Implement site blacklsting
- PGP/GPG integrity checking
- Implement site banners/avatars
- Webring page generation
- Peer and site removal
- Administrative web interface
- Support for different languages to make it easier to update data directly from webserver
- Daemon that checks for events across the webring such as site additions, removal, and peer connections
- Possibly support scraping of popular webrings to allow for easy import of existing data
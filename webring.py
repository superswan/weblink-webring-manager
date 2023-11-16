import argparse
import requests
import json
import os
import base64

def load_or_initialize_webring():
    file_path = 'webring.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    
    return initialize_webring()

# Manually add a site entry
def create_site_entry(is_node):
    title = input("Enter the title of your site: ")
    url = input("Enter your site URL: ")
    if is_node:
        ring_url = input("Enter the webring URL path (Leave blank to set as root): ")
    else:
        ring_url = "None"

    if not ring_url:
        ring_url = url

    image_path = input("Enter the local path to your banner image (leave blank if none): ")
    avatarb64 = ""
    if image_path:
        with open(image_path, "rb") as image_file:
            avatarb64 = base64.b64encode(image_file.read()).decode('utf-8')

    return {
        "title": title,
        "url": url,
        "ring_url": ring_url,
        "avatarb64": avatarb64,
        "gpg": "public_key",  # Placeholder for GPG key
    }

# Used for configuring the local node
def create_node_entry():
    node_data = create_site_entry(True)
    master_node_url = input("Enter the master node URL (leave blank if none): ")
    node_data["master_node_url"] = master_node_url
    node_data["blacklist"] = []

    return node_data

def initialize_webring():
    node_config = create_node_entry()
    webring_data = {
        "node": node_config,
        "sites": []  # Initialize empty sites list
    }

    with open('webring.json', 'w') as file:
        json.dump(webring_data, file, indent=4)
    
    print("\nCreated JSON data file")

    master_node_url = node_config.get("master_node_url")
    if master_node_url:
        print(f"Adding master node: {master_node_url}")
        add_peer(master_node_url)
        sync_peer_data(master_node_url)

    return webring_data
    
def get_master_node_url(data):
    if 'node' in data and data['node']:
        return data['node'].get('master_node_url', '')
    return None

def fetch_webring_data(url):
    if 'http://' not in url or 'https://' not in url:
        url = 'http://' + url
    url = url + '/webring.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

# Appends node data to local sites array
def add_peer(webring_url):
    print(f"Fetching webring data from {webring_url}")
    remote_data = fetch_webring_data(webring_url)
    if not remote_data or "node" not in remote_data:
        print("Invalid or empty data from remote node.")
        return []

    remote_node_data = remote_data["node"]
    remote_node_site_data = {
        "title": remote_node_data['title'],
        "url": remote_node_data['url'],
        "ring_url": remote_node_data['ring_url'],
        "avatarb64": remote_node_data['avatarb64'],
        "gpg": "public_key",  # Placeholder for GPG key
    }

    with open('webring.json', 'r') as file:
        local_data = json.load(file)

    local_node_url = local_data['node']['url']
    if remote_node_data['url'] is not local_node_url:
        local_data["sites"].append(remote_node_site_data)

    with open('webring.json', 'w') as file:
        json.dump(local_data, file, indent=4)

    print(f"Successfully added peer {remote_node_data['title']}({remote_node_data['ring_url']})")
    return local_data["sites"]

# Add missing sites from peer sites array to the local sites array
def sync_peer_data(webring_url):
    remote_data = fetch_webring_data(webring_url)

    if not remote_data or "sites" not in remote_data:
        print("Invalid or empty data from remote node.")
        return []

    remote_site_title = remote_data["node"]['title']
    remote_sites_data = remote_data["sites"]

    print(f"Syncing site data from node -- {remote_site_title}")
    with open('webring.json', 'r') as file:
        local_data = json.load(file)

    local_node_url = local_data['node']['url']
    local_sites_urls = {site['url'] for site in local_data['sites']}

    for site in remote_sites_data:
        if site['url'] not in local_sites_urls and site['url'] != local_node_url:
            local_data['sites'].append(site)

    with open('webring.json', 'w') as file:
        json.dump(local_data, file, indent=4)

    return local_data['sites']

def main():
    parser = argparse.ArgumentParser(description="Webring Management Script")
    subparsers = parser.add_subparsers(dest='command')

    # Subparser for addpeer
    parser_addpeer = subparsers.add_parser('addpeer', help='Add a new peer to the webring')
    parser_addpeer.add_argument('url', help='URL of the peer to add')

    # Subparser for syncpeer
    parser_syncpeer = subparsers.add_parser('syncpeer', help='Synchronize peer data')
    parser_syncpeer.add_argument('url', nargs='?', default='', help='URL of the peer to sync with (optional)')

    # Subparser for addsite
    subparsers.add_parser('addsite', help='Add a new site to the webring')

    args = parser.parse_args()

    # commands should be seperated into functions in future versions
    if args.command == 'addpeer':
        add_peer(args.url)
    elif args.command == 'syncpeer':
        if args.url:
            sync_peer_data(args.url)
        else:
            with open('webring.json', 'r') as file:
                webring_data = json.load(file)
            remote_ring_urls = {site['ring_url'] for site in webring_data['sites']}
            for ring_url in remote_ring_urls:
                if ring_url != "None":
                    sync_peer_data(ring_url)
    elif args.command == 'addsite':
        site = create_site_entry(False)
        with open('webring.json', 'r') as file:
            local_data = json.load(file)

        local_node_url = local_data['node']['url']   
        local_sites_urls = {site['url'] for site in local_data['sites']}
        if site['url'] not in local_sites_urls and site['url'] != local_node_url:
            local_data['sites'].append(site)
        
        with open('webring.json', 'w') as file:
            json.dump(local_data, file, indent=4)
    else:
        webring_data = load_or_initialize_webring()
        with open('webring.json', 'r') as file:
            webring_data = json.load(file)
        print(json.dumps(webring_data, indent=4))

if __name__ == "__main__":
    main()

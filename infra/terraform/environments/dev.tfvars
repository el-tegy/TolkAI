# GCP Project ID
project = "just-lore-408910"

# GCP Project Region
region = "us-west4" # This one is Las Vegas, Nevada, Amérique du Nord

# GCP Credentials Key File JSON
credentials = "./environments/credentials.json"

# Number of nodes 
num_nodes = 4

# Path to the public SSH key
public_key_path = "/home/samuel/.ssh/id_rsa.pub"

# List of IP addresses to whitelist in the firewall
whitelisted_ips = ["0.0.0.0/0"]

# List of ports to whitelist in the firewall
whitelisted_ports = []

# List of Common Labels
common_labels = {
  owner       = "gocod"
  deployed_by = "terraform"
}

# Username for the VM instances(this one is replaced by the script init-deploy.sh)
username = "ladibesamuel"
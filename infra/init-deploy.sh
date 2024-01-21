#!/bin/bash

# Check for the correct number of arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <environment> <username> <local_private_key_path>"
    exit 1
fi
ENVIRONMENT=$1
USERNAME=$2
PRIVATE_KEY_PATH=$3

# Function to update Ansible inventory with dynamic IPs
update_ansible_inventory() {
  local db="$1"
  shift
  local ips=("$@")
  #ls 
  echo "[${db}_cluster]" > ansible/inventory/$db.ini
  for i in "${!ips[@]}"; do
    ssh-keygen -f "$HOME/.ssh/known_hosts" -R "${ips[i]}"
    echo "${db}-node-$i ansible_host=${ips[i]}" >> ansible/inventory/$db.ini
  done

  # Add other groups and vars as needed
  echo "[${db}_cluster:vars]" >> ansible/inventory/$db.ini
  echo "ansible_user=$USERNAME" >> ansible/inventory/$db.ini
  echo "ansible_ssh_private_key_file=$PRIVATE_KEY_PATH" >> ansible/inventory/$db.ini
}

# Navigate to Terraform directory and apply configurations
cd terraform
sed -i "s/username = \"username_to_replace\"/username = \"${USERNAME}\"/" environments/$ENVIRONMENT.tfvars
terraform init
terraform apply -var-file="environments/$ENVIRONMENT.tfvars"

# Capture output IPs from Terraform
streamlit_ips=$(terraform output -json streamlit_instance_ips | jq -r '.[]')

# Revert Terraform variable file to original state
sed -i "s/username = \"${USERNAME}\"/username = \"username_to_replace\"/" environments/$ENVIRONMENT.tfvars
cd ..

# Run Ansible playbooks
#cd ansible

###############################
#            streamlit        # 
###############################
# Update Ansible inventory with streamlit IP addresses
update_ansible_inventory "streamlit" $streamlit_ips
# Install docker 
ansible-playbook -i ./inventory/streamlit.ini ./ansible/tasks/docker.yml
# Install streamlit 
ansible-playbook -i ./inventory/streamlit.ini ./ansible/tasks/streamlit.yml
# Infrastructure GCP Deployment

This repository contains Terraform configurations and Ansible playbooks to deploy infrastructure resources on Google Cloud Platform (GCP).

## Prerequisites

Before beginning, ensure you have the following:
- A Google Cloud Platform account with billing enabled(Use for 300$ free credits).
- Terraform installed on your machine ([Installation Guide](https://www.terraform.io/downloads.html)). 
- Ansible installed on your machine ([Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)).
> Ansible and Terraform are already installed in the dev container.
## Getting Started

### 1. **GCP Setup:**
   - Create a new GCP project through the [GCP Console](https://console.cloud.google.com/projectcreate).
   - Enable Compute Engine API for your project [there](https://console.cloud.google.com/marketplace/product/google/compute.googleapis.com?).
   - Create a service account with necessary permissions (Compute Admin, etc.) and download the JSON key filein [IAM Service](https://console.cloud.google.com/iam-admin/serviceaccounts?).
   > Some resources if you're lost:
   > - [What are Service Accounts?](https://www.youtube.com/watchv=xXk1YlkKW_k)
   > - [Generate service account key](https://www.youtube.com/watch?v=dj9fxiuz4WM)


### 2. **Local setup:**
**Generate a SSH key**

Get into the dev container and generate an ssh key.
Keep the public and private paths of this generated key pair. 

```bash
ssh-keygen
```
Type enter 3 times(for filename, passphrase and confirm passphrase). 
You'll hav an output like this:
```
The key's randomart image is:
+---[RSA 3072]----+
|o=oo.            |
|. =.    .        |
|=ooo   .o.       |
|Bo..o..+.oo      |
|.. =oo*oSo       |
|  ooo= =+o       |
|  .== *...       |
|   ++o o  .      |
|    .     .E     |
+----[SHA256]-----+
root@ac22d551d53d:/#
```
You key files path's will looks like: `/home/devcontainer/.ssh/id_rsa*`.

It will be usefull for ansible to connect in ssh in your terraform provisionate VMs in order to install packages.


   
**Navigate to the infra section of the repo**
> Make sure you pulled the latest changes from the GoCod repo.
   ```bash
   cd infra
   ```
You'll get into this directory:
```
.
├── README.md
├── ansible/
├── terraform/
└── init-deploy.sh
```

- `terrform` host what you need to handle cloud resources provisionning especially Virtual Machines. The ones that will host your databases. You'll be able to add other resources like CloudRun, Secrets, etc... given your needs.

- `ansible` host what you need to handle configurations of Virtual Machines.

- `init-deploy.sh` is a script that helps you run the minimal provisionning and some configurations.

3. **Configure Terraform:**
   - Navigate to the `terraform/` directory.
   - In the file `environments/dev.tfvars` that you can create from the example one, Set the right values that are used into the terraform files like `main.tf` and `streamlit.tf`.
   - Review, complete and modify `streamlit.tf` to suit your instance requirements (e.g., machine type, region). You can add variables if needed. 
   
   > **TODO:** There are 4 mentions "TO COMPLETE" to make you add some relevant configurations by yourselves. Find them and complete them.

4. **Initialize Terraform:**
Once you completed the files `environments/dev.tfvars` and `streamlit.tf`, you can start provisioning.
   ```bash
   cd terraform
   terraform init
   ```

5. **Apply Terraform Configuration:**
   ```bash
   terraform apply -var-file="environments/dev.tfvars"
   ```
   - Confirm the changes by typing `yes` when prompted.

6. **Update Ansible Inventory:**
   - Navigate to the `ansible/` directory.
   - Create a streamlit inventory named `streamlit.ini` from the example `inventory.ini` with the external IP addresses of the created GCP instances (replace `INSTANCE_IP_0`, `INSTANCE_IP_1`, etc.).

7. **Run Ansible Playbook:**
   - The command will install docker on the remote server
   ```bash
   ansible-playbook -i inventory/streamlit.ini tasks/docker.yml
   ```
   - This will install and start streamlitDB using Docker on the GCP instances. Let's reming that the way this installation is done is not the good one and you'll have to change it.
   ```bash
   ansible-playbook -i inventory/streamlit.ini tasks/streamlit.yml
   ```

8. **Check if you can reach the database**

Let's image INSTANCE_IP_0 value is `34.155.143.166`, you'll run the command:
   ```bash
curl 34.155.143.166:27017
   ```
The output if you have access will be:
```
It looks like you are trying to access streamlitDB over HTTP on the native driver port.
```
Once you have that, you can try trun the deployement script using:
```bash
#set permissions to execute this script(dot it once)
chmod +x ./init-deploy.sh
#run the script
./init-deploy.sh dev admin $HOME/.ssh/id_rsa
# "dev" is for the environement(it's the name you gave to your variables file)
# "admin" is the username to use in the VMs
# "$HOME/.ssh/id_rsa" is the path to your private ssh key
```
In this case your streamlit URI usable to connect to your database is `streamlitdb://34.155.143.166:27017`, which is not safe as there is no **Network** nor **Database** Access configured.

You will then have to make this more secure with managing **Network Access with Terraform** and **Database access with Ansible**. The same should be done for Neo4j.


resource "google_compute_firewall" "streamlit_firewall_rule" {
  name    = "streamlit-allow-specific-ips-on-ports"
  network = "default"

  allow {
    protocol = "tcp"
    ports = ["8501"] # Port Management
  }

  source_ranges = var.whitelisted_ips # IP Whitelisting
  target_tags   = ["http-server","https-server"] # Firewall rule applies only to instances with this tag
}


resource "google_compute_instance" "streamlit_node" {
  count        = var.num_nodes # the number of instances to provision
  name         = "streamlit-node-${count.index}"
  machine_type = "e2-medium" # machine type of each node, for GPU machine use n2-standard-2
  zone = "us-west4-a" # The instance zone(not the region)
  tags         = ["http-server","https-server"] # Tags to connect instances to internet
  # allow_stopping_for_update = true
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11" #OS for each VM
      size   = 20   # specify the size of the disk in GB
      labels = var.common_labels # Some labels to identify the resources
    }
  }

  network_interface {
    network = "default"
    access_config {
      
    }
  }
  metadata_startup_script = <<-EOF
                              echo "Creating user ${var.username}"
                              sudo useradd -m -s /bin/bash -G sudo ${var.username}
                              echo "Deactivating password for user ${var.username}"
                              sudo passwd -d ${var.username}

                              sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/google-test-disk
                              sudo mkdir -p /streamlit/data
                              sudo mount -o discard,defaults /dev/disk/by-id/google-test-disk /streamlit/data
                              sudo chown -R ${var.username}:${var.username} /streamlit/data
                              echo UUID=$(sudo blkid -s UUID -o value /dev/disk/by-id/google-test-disk) /streamlit/data ext4 discard,defaults,nofail 0 2 | sudo tee -a /etc/fstab

                              EOF
    metadata = {
    ssh-keys = "${var.username}:${file(var.public_key_path)}"
  }
}

# Persistant disk for external storage
resource "google_compute_disk" "streamlit_disk" {
  count = var.num_nodes
  name = "streamlit-disk-${count.index}"
  type = "pd-standard"
  zone = "us-west4-a"
  size = 5 # specify the size of the disk in GB
  labels = {
    environment = "dev"
  }
  physical_block_size_bytes = 4096
}

resource "google_compute_attached_disk" "streamlit_attached_disk" {
  count = var.num_nodes
  disk     = google_compute_disk.streamlit_disk[count.index].id
  instance = google_compute_instance.streamlit_node[count.index].id
  zone     = google_compute_instance.streamlit_node[count.index].zone
}

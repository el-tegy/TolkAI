### Managed Instance Group
# First, wrap google_compute_instance resources in a Managed Instance Group (MIG) to allow the Load Balancer to automatically manage and scale the instances:

resource "google_compute_instance_template" "streamlit_template" {
  name_prefix   = "streamlit-template-"
  machine_type  = "e2-medium"
  tags          = ["http-server", "https-server"]

  disk {
    source_image = "debian-cloud/debian-11"
    auto_delete  = true
    boot         = true
    disk_size_gb = 20
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    ssh-keys            = "${var.username}:${file(var.public_key_path)}"
    startup-script      = <<EOF
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
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_compute_instance_group_manager" "streamlit_mig" {
  name               = "streamlit-mig"
  base_instance_name = "streamlit"
  zone               = "us-west4-a"
  target_size        = var.num_nodes

   version {
    instance_template = google_compute_instance_template.streamlit_template.self_link
  }
}


### HTTP(S) Load Balancer
# Add the HTTP(S) Load Balancer resources, including a backend service, URL map, target HTTP proxy, and a global forwarding rule:

resource "google_compute_health_check" "streamlit_health_check" {
  name               = "streamlit-health-check"
  check_interval_sec = 30
  timeout_sec        = 10
  tcp_health_check {
    port = 8501
  }
}

resource "google_compute_backend_service" "streamlit_backend_service" {
  name        = "streamlit-backend-service"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 10
  health_checks = [google_compute_health_check.streamlit_health_check.self_link]
}

resource "google_compute_url_map" "streamlit_url_map" {
  name            = "streamlit-url-map"
  default_service = google_compute_backend_service.streamlit_backend_service.self_link
}

resource "google_compute_target_http_proxy" "streamlit_http_proxy" {
  name    = "streamlit-http-proxy"
  url_map = google_compute_url_map.streamlit_url_map.self_link
}

resource "google_compute_global_forwarding_rule" "streamlit_forwarding_rule" {
  name       = "streamlit-http-forwarding-rule"
  target     = google_compute_target_http_proxy.streamlit_http_proxy.self_link
  port_range = "80"
}


### Update Firewall Rules
# Ensure firewall rules allow traffic from the load balancer. You may need to adjust your existing google_compute_firewall resource or add a new one to allow traffic from Google's load balancer IP ranges (130.211.0.0/22 and 35.191.0.0/16):
resource "google_compute_firewall" "lb-to-instances" {
  name    = "allow-lb-to-instances"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8501"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
  target_tags   = ["http-server", "https-server"]
}
#!/bin/bash
set -e

# Create static directory
sudo mkdir -p /var/www/jobmatch/static
sudo cp /tmp/manifest.json /var/www/jobmatch/static/
sudo cp /tmp/sw.js /var/www/jobmatch/static/
sudo chown -R www-data:www-data /var/www/jobmatch/static
sudo chmod 644 /var/www/jobmatch/static/*

# Find nginx config
if [ -f /etc/nginx/sites-available/jobmatch ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/jobmatch"
elif [ -f /etc/nginx/sites-available/default ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/default"
else
    echo "❌ Could not find nginx config"
    exit 1
fi

# Backup config
sudo cp "$NGINX_CONFIG" "$NGINX_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"

# Check if static file locations already exist
if grep -q "location = /manifest.json" "$NGINX_CONFIG"; then
    echo "⚠️  Static file locations already exist, updating..."
    # Remove old entries
    sudo sed -i '/location = \/manifest.json/,/^    }$/d' "$NGINX_CONFIG"
    sudo sed -i '/location = \/sw.js/,/^    }$/d' "$NGINX_CONFIG"
fi

# Add static file locations before the main location block
sudo sed -i '/location \/ {/i\
    # Static files - manifest.json and sw.js\
    location = /manifest.json {\
        root /var/www/jobmatch/static;\
        add_header Content-Type "application/manifest+json";\
        add_header Cache-Control "public, max-age=3600, must-revalidate";\
        access_log off;\
    }\
\
    location = /sw.js {\
        root /var/www/jobmatch/static;\
        add_header Content-Type "application/javascript";\
        add_header Service-Worker-Allowed "/";\
        add_header Cache-Control "public, max-age=3600, must-revalidate";\
        access_log off;\
    }\
' "$NGINX_CONFIG"

# Test nginx config
if sudo nginx -t; then
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded successfully"
else
    echo "❌ Nginx config test failed"
    exit 1
fi


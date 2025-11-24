#!/bin/bash
# Remove all JSON fragments from .env file

cd /opt/jobmatch || exit 1

# Backup .env
cp .env .env.backup

# Remove all lines that look like JSON fragments
sed -i '/"type":/d' .env
sed -i '/"project_id":/d' .env
sed -i '/"private_key_id":/d' .env
sed -i '/"private_key":/d' .env
sed -i '/"client_email":/d' .env
sed -i '/"client_id":/d' .env
sed -i '/"auth_uri":/d' .env
sed -i '/"token_uri":/d' .env
sed -i '/BEGIN PRIVATE KEY/d' .env
sed -i '/END PRIVATE KEY/d' .env
sed -i '/^-----/d' .env
sed -i '/^  "/d' .env
sed -i '/^    "/d' .env

echo "✅ JSON fragments removed from .env"


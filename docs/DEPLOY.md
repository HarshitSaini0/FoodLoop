# Deploy on an Oracle Cloud free Ubuntu server

Assumes Ubuntu with Apache already serving your DuckDNS domain. Replace names to match your setup.

## 1. Get the code and run it once

```bash
cd ~ && git clone https://github.com/<you>/foodloop.git && cd foodloop
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

Optional: copy a trained `model/model.pt` to the server with `scp` (it is not in git).

## 2. Set a password (do this before it is public)

```bash
cat > .env <<'EOF'
FOODLOOP_USER=judge
FOODLOOP_PASSWORD=choose-a-long-random-password
EOF
chmod 600 .env
```

The app asks for HTTP Basic login only when both variables are set. Share the login only with people you want to see the demo.

## 3. Run as a service

```bash
sudo cp deploy/foodloop.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now foodloop
systemctl status foodloop
curl -s http://127.0.0.1:8001/health      # needs -u user:pass if auth is on
```

Edit `User=` and paths in the unit file if your user is not `ubuntu`.

## 4. Subdomain and Apache

In DuckDNS add a subdomain (for example `foodloop-harshit`) pointing to the server IP, then put that name in `deploy/apache-foodloop.conf`.

```bash
sudo a2enmod proxy proxy_http headers
sudo cp deploy/apache-foodloop.conf /etc/apache2/sites-available/foodloop.conf
sudo a2ensite foodloop && sudo apache2ctl configtest && sudo systemctl reload apache2
```

## 5. Open the ports

Oracle blocks traffic in two places. Allow TCP 80 and 443 in the VCN security list (Ingress rules), and on the instance:

```bash
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

Skip any you already opened for your other sites.

## 6. HTTPS

```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d <your-subdomain>.duckdns.org
```

## Notes

- Uploaded photos and the SQLite ledger live in `data/`. Back it up or wipe it before showing the demo.
- Use demo photos only. Do not upload photos of people or anything private.
- Update: `git pull && sudo systemctl restart foodloop`.
- If you already run other apps on port 8001, change the port in both the service file and the Apache config.

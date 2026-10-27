# Deployment

## One computer, offline

Download and extract a release ZIP; run `python3 server.py`; open http://127.0.0.1:8080. Only Python 3.11+ and a modern browser are required. The app makes no external requests. Internet is needed only for download or updates. A running local server is still required; this release does not include a service worker or installable PWA.

Use `--port 8081` if 8080 is occupied. Stop with Ctrl+C. No admin/root privileges or account setup are required. Printing uses the browser print dialog and supports PDF or paper. The plain Markdown in `content/` can also be read without the app.

## A trusted classroom LAN

Use an existing network managed by an authorized local administrator. This kit does not configure access points, DNS, VPNs or firewall rules. On the host, identify its actual LAN IPv4 address, then run, for example:

```sh
python3 server.py --bind 0.0.0.0 --port 8080 --allow-host 192.168.1.25
```

Replace the example with the host's real address. Learners on that network open `http://192.168.1.25:8080`. Add another `--allow-host school.local` only if local DNS resolves that name. Stop the process to end sharing. The server requires an explicit allowed host for non-loopback binding. Loopback names remain allowed.

Every served document and teacher key is readable by anyone who can reach the server. There is no login, TLS or teacher permission boundary. Notes remain in each browser; sharing a browser profile shares its notes. Avoid untrusted/public networks and student personal data. Test reachability on the actual local network before relying on it. Local network policies and equipment costs are the adopter's responsibility.

## Public static website

```sh
python3 scripts/build.py --output site
```

Upload the entire `site/` directory to a maintained static HTTPS host of your choice. All links and assets are relative, so subdirectory hosting works. The host receives normal web requests and may have its own logging policy; the app has no analytics. Notes are local to that exact origin and browser. Source hosting on GitHub does not itself deploy a website.

## Update, rollback and backup

Export personal notes before changing origins/browsers or clearing browser storage. Download a new release into a separate folder, run the tests, stop the old server and start the new one. Keep the prior folder to roll back. A build error must be fixed before distribution. Restore exported notes with Import notes; import merges by lesson ID after a visible review and explicit confirmation.

SHA-256 checksums accompany releases. Check the ZIP against `SHA256SUMS` after transferring it by USB. This detects corruption relative to the downloaded checksum; it does not independently authenticate the publisher.

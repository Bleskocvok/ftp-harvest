# FTP-Harvest

An automatic tool that synchronizes your files with an FTP server.

Create a file named `harvestlist.txt` to keep a list of all files this script should sync.

```bash
python3 ftp-harvest/run.py
```

## Environment variables

Uses the Python library **dotenv** which allows to set up environment variables inside a file `.env`.

Specify these variables to connect to an FTP server:

- `FTP_SERVER` - **must** be specified; contains the FTP url to connect to
- `FTP_PORT` - unless specified uses the default port 21
- `FTP_USERNAME`
- `FTP_PASSWORD`


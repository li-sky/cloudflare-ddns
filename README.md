# Cloudflare DDNS

This project is a dynamic DNS (DDNS) updater for Cloudflare. With minimal requirement (only requires `requests`, it allows you to automatically update your DNS records on Cloudflare with your current IP address.

## Installation

1. Clone this repository: `git clone https://github.com/li-sky/cloudflare-ddns.git`
2. Install the required dependencies: `pip install -r ./requirements.txt` (or, if your python packages are managed by system-wide package manager, you may need to install the package with your package manager)
3. Configure the project by editing the `config.json` file.

## Configuration

In order to use this project, you need to provide your Cloudflare API credentials and specify the DNS record you want to update. Open the `config.json` file and fill in the following information:

```json
{
    "logging": {
        "level": "info",
        "file": "/path/to/dns-proxy.log"
    },
    "token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "zone_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "records": [
        {
            "type" : "A",
            "name" : "your-record.domain.tld",
            "isLocal" : true,
            "interface" : "Ethernet",
            "matchregex" : "192.*"
        },
        {
            "type" : "AAAA",
            "name" : "your-record.domain.tld",
            "isLocal" : true,
            "interface" : "Ethernet",
            "matchregex" : "2001:da8::*"
        },
        {
            "type" : "A",
            "name" : "your-record.domain.tld",
            "isLocal" : false,
            "interface" : "Ethernet"
        },
        {
            "type" : "AAAA",
            "name" : "your-record.domain.tld",
            "isLocal" : false,
            "interface" : "Ethernet"
        }
    ]
}
```

## Usage

Once you have configured the project, you can run the updater by executing the following command:

```bash
python ./cloudflare-ddns.py
```

The updater will automatically retrieve your current IP address and update the specified DNS record on Cloudflare one single time. To run the updater every 5 minutes, you can use a cron job:

```bash
*/5 * * * * /usr/bin/python3 /path/to/cloudflare-ddns/cloudflare-ddns.py
```

Or, if you are under windows, you can use the task scheduler to run the script every 5 minutes.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the GPLv3 license. See the [LICENSE](LICENSE) file for more information. (Acutally I don't really care lol)

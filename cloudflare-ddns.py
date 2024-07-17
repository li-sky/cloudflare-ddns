import requests
import logging
import sys

def argp(args):
    import argparse
    parser = argparse.ArgumentParser(description='Update Cloudflare DNS record with current public IP address')
    parser.add_argument('-c', '--config', help='Path to config file', default='config.json')
    ret = parser.parse_args(args)
    return ret

def configParse(configPath):
    import json
    with open(configPath, 'r') as configFile:
        config = json.load(configFile)
        return config

def genID():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

def main(args):
    parsed_args = argp(args)
    config = configParse(parsed_args.config)
    # setup log file
    # get log level
    if "logging" in config:
        if "level" in config["logging"]:
            logLevel = config["logging"]["level"]
        else:
            logLevel = "INFO"
        logging.basicConfig(filename=config["logging"]["file"], level = logLevel)
    else:
        logging.basicConfig()
    headers = {
        'Authorization': 'Bearer {}'.format(config['token']),
        'Content-Type': 'application/json'
    }
    # fetch DNS record
    url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(config['zone_id'])
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    record = data['result']
    for localSetting in config["records"]:
        # Prepare content of record
        content = ""
        if localSetting["isLocal"]:
            # use local setting
            if sys.platform == "win32":
                # use Powershell to fetch ips
                import subprocess
                import json
                ip = subprocess.run(["powershell", "-Command", "Get-NetIPAddress | ConvertTo-JSON"], capture_output=True, text=True)
                ip = json.loads(ip.stdout)
                for localIPRecord in ip:
                    # if we have regex
                    import re
                    if (
                        ("matchregex" in localSetting and
                        re.search(localSetting["matchregex"], localIPRecord["IPAddress"]) and
                        localSetting["interface"] == localIPRecord["InterfaceAlias"]) or
                        ("matchregex" not in localSetting and
                         localSetting["interface"] == localIPRecord["InterfaceAlias"])
                    ):
                        content = localIPRecord["IPAddress"]
                        break
            elif str(sys.platform).startswith("linux"):
                import subprocess
                import json
                ip = subprocess.run(["ip", "-j", "addr"], capture_output=True, text=True)
                ip = json.loads(ip.stdout)
                for localIPRecord in ip:
                    if localIPRecord["ifname"] == localSetting["interface"]:
                        for ipentry in localIPRecord["addr_info"]:
                            import re
                            if (re.search(localSetting["matchregex"], ipentry["local"])):
                                content = ipentry["local"]
                                break
        else:
            # use web api for ip
            if localSetting["type"] == "A":
                response = requests.get("https://api.ipify.org")
                content = response.text
            elif localSetting["type"] == "AAAA":
                response = requests.get("https://api6.ipify.org")
                content = response.text
        if content == "":
            logging.debug("No IP found for record: {} {}".format(localSetting["type"], localSetting["name"]))
            continue

        # update record
        recordUpdateSuccess = False
        for DNSRecord in record:
            if localSetting["type"] == DNSRecord["type"] and localSetting["name"] == DNSRecord["name"]:
                # update record
                recordUpdateSuccess = True
                url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(config['zone_id'], DNSRecord['id'])
                response = requests.patch(url, headers=headers, json={
                    'type': DNSRecord['type'],
                    'name': DNSRecord['name'],
                    'content': content,
                    "proxied": False,
                    'id': DNSRecord['id'],
                    'ttl': DNSRecord['ttl']
                })
                response.raise_for_status()
                logging.debug("Updated record: {} {} to {}".format(localSetting["type"], localSetting["name"], content))
                break
        if not recordUpdateSuccess:
            # create record
            url = 'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(config['zone_id'])
            response = requests.post(url, headers=headers, json={
                'type': localSetting["type"],
                'name': localSetting["name"],
                'content': content,
                "proxied": False,
                'ttl': 1,
                'id': genID()
            })
            print(response.content)
            response.raise_for_status()
            logging.debug("Created record: {} {} to {}".format(localSetting["type"], localSetting["name"], content))
    

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

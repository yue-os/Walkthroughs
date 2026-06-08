# Biohazard CTF Walkthrough - TryHackMe

[Link to Room](https://tryhackme.com/room/biohazard)

## 1. Challenge Overview
**Name:** Biohazard
**Platform:** TryHackMe
**Category:** Web / Recon
**Difficulty:** Medium

## Phase 1: Reconnaissance

### Nmap Scan
Initial scanning reveals three open ports:
- **21/tcp:** FTP (vsftpd 3.0.3)
- **22/tcp:** SSH (OpenSSH 7.6p1)
- **80/tcp:** HTTP (Apache 2.4.29)

### Web Enumeration
The homepage (`http://biohazard/`) introduces the **STARS alpha team** (Chris, Jill, Barry, Wesker, Joseph) searching for the **STARS bravo team**.

**Answers:**
- How many open ports? **3**
- What is the team name in operation? **STARS alpha team**

---

## Phase 2: The Mansion (Item & Flag Hunting)

### 1. Emblem Flag
Visit `http://biohazard/mansionmain/` -> `http://biohazard/diningRoom/` -> `emblem.php`.
- **Flag:** `emblem{fec832623ea498e20bf4fe1821d58727}`

### 2. Lock Pick Flag
The source code of `/diningRoom/` contains a Base64 hint: `SG93IGFib3V0IHRoZSAvdGVhUm9vbS8=` (`/teaRoom/`).
Visit `http://biohazard/teaRoom/` -> `master_of_unlock.html`.
- **Flag:** `lock_pick{037b35e2ff90916a9abf99129c8e1837}`

### 3. Music Sheet Flag
Visit `http://biohazard/barRoom/`. Use the **lock pick flag** to unlock the door. 
Read `musicNote.html` and decode the Base32 string:
`NV2XG2LDL5ZWQZLFOR5TGNRSMQ3TEZDFMFTDMNLGGVRGIYZWGNSGCZLDMU3GCMLGGY3TMZL5`
- **Flag:** `music_sheet{362d72deaf65f5bdc63daece6a1f676e}`

### 4. Gold Emblem Flag
In the Bar Room, enter the **music sheet flag** to unlock `barRoomHidden.php`. 
Take the Gold Emblem.
- **Flag:** `gold_emblem{58a8c41a9d08b8a4e38d02a4d7ff4843}`

### 5. Shield Key Flag
Enter the **emblem flag** in the slot at `barRoomHidden.php` to get the hint **rebecca**.
Return to `/diningRoom/` and enter the **gold emblem flag**. This reveals a Vigenere cipher:
`klfvg ks r wimgnd biz mpuiui ulg fiemok tqod. Xii jvmc tbkg ks tempgf tyi_hvgct_jljinf_kvc`
Using key **rebecca**, it decodes to: `there is a second map inside the dining room. The link name is called the_great_shield_key_htm`
Visit `http://biohazard/diningRoom/the_great_shield_key.html`.
- **Flag:** `shield_key{48a7a9227cd7eb89f0a062590798cbac}`

### 6. Blue Gem Flag
In `http://biohazard/diningRoom2F/`, the source code has a ROT13 hint pointing to `sapphire.html`.
Visit `http://biohazard/diningRoom/sapphire.html`.
- **Flag:** `blue_jewel{e1d457e96cac640f863ec7bc475d48aa}`

---

## Phase 3: The Crest Hunting & FTP Access

### FTP Credentials
Four "crests" are found and decoded:
1. **Crest 1:** (`tigerStatusRoom`) Decoded Base64 -> Base32: `RlRQIHVzZXI6IG`
2. **Crest 2:** (`galleryRoom`) Decoded Base32 -> Base58: `h1bnRlciwgRlRQIHBh`
3. **Crest 3:** (`armorRoom`) Decoded Base64 -> Binary -> Hex: `c3M6IHlvdV9jYW50X2h`
4. **Crest 4:** (`attic`) Decoded Base58 -> Hex: `pZGVfZm9yZXZlcg==`

**Combined Base64:** `RlRQIHVzZXI6IGh1bnRlciwgRlRQIHBhc3M6IHlvdV9jYW50X2hpZGVfZm9yZXZlcg==`
**Decoded:** `FTP user: hunter, FTP pass: you_cant_hide_forever`

**Answers:**
- FTP Username: **hunter**
- FTP Password: **you_cant_hide_forever**

---

## Phase 4: The Guard House (Forensics)

Download files from FTP: `001-key.jpg`, `002-key.jpg`, `003-key.jpg`, `helmet_key.txt.gpg`, `important.txt`.

### Solving the Encrypted Password
1. **Key 1:** `steghide extract -sf 001-key.jpg` -> `cGxhbnQ0Ml9jYW`
2. **Key 2:** `exiftool 002-key.jpg` (Comment) -> `5fYmVfZGVzdHJveV9`
3. **Key 3:** `binwalk -e 003-key.jpg` -> `3aXRoX3Zqb2x0`

**Full Base64:** `cGxhbnQ0Ml9jYW5fYmVfZGVzdHJveV93aXRoX3Zqb2x0`
**Decoded Password:** **plant42_can_be_destroy_with_vjolt**

### Decrypting the Helmet Key
`gpg --batch --passphrase "plant42_can_be_destroy_with_vjolt" --decrypt helmet_key.txt.gpg`
- **Flag:** `helmet_key{458493193501d2b94bbab2e727f8db4b}`

**Answers:**
- Hidden directory mentioned by Barry: **/hidden_closet/**
- Password for encrypted file: **plant42_can_be_destroy_with_vjolt**
- Helmet Key flag: **helmet_key{458493193501d2b94bbab2e727f8db4b}**

---

## Phase 5: The Revisit (SSH Access)

### 1. SSH Credentials
Visit `http://biohazard/studyRoom/`, unlock with **helmet key flag**, download `doom.tar.gz`.
Extract it: `eagle_medal.txt` reveals SSH user **umbrella_guest**.
Visit `http://biohazard/hidden_closet/` (unlock with helmet key flag) to find `wolf_medal.txt`.
- **SSH Username:** **umbrella_guest**
- **SSH Password:** **T_virus_rules**

### 2. STARS Bravo Team Leader
Description in `/hidden_closet/` mentions **Enrico Marini**.
- **STARS Bravo Team Leader:** **Enrico Marini**

---

## Phase 6: Underground Laboratory (Final Showdown)

### 1. Traitor & Location
Login as `umbrella_guest`. Check `.jailcell/chris.txt`.
- Where you found Chris: **Jail cell**
- Who is the traitor: **Wesker** (Albert Wesker)
- Hint: MO Disk 2 key is **albert**.

### 2. Wesker's Password
Decipher `MO_DISK1.txt` (from `hidden_closet`) using Vigenere key **albert**:
`wpbwbxr wpkzg pltwnhro, txrks_xfqsxrd_bvv_fy_rvmexa_ajk` -> `weasker login password, stars_members_are_my_guinea_pig`
- **Wesker Password:** **stars_members_are_my_guinea_pig**

### 3. Final Flag
Login as `weasker`. Read `weasker_note.txt` to find the ultimate form: **Tyrant**.
Use sudo to read the root flag: `sudo cat /root/root.txt`.
- **Name of the ultimate form:** **Tyrant**
- **Root Flag:** **3c5794a00dc56c35f2bf096571edf3bf**

---

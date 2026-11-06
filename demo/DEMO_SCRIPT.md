# Event Volunteer Desk — Demo Walkthrough Script

This script walks through an end-to-end interactive simulation between **Organiser Priya**, **Volunteer Rohan**, and the **AI Agent (@volunteer-bot)** inside the Switch `#volunteer-desk` room.

---

## 👥 Persona Setup
* **Account 1 (Organiser):** `priya_lead` (Event Chairperson, HackAvadh 2026)
* **Account 2 (Volunteer):** `rohan_tech` (Student Volunteer, Amity Lucknow)
* **AI Agent:** `@volunteer-bot` (Powered by Switch & Antigravity)

---

## 🎬 Scene 1: Organiser Posts a Staffing Need

**User:** `priya_lead` (Top-level message in `#volunteer-desk`)
```text
@volunteer-bot We have a huge rush expected at check-in on Saturday morning! We need 4 people at Registration & Check-in from 9:00 AM to 1:00 PM, and 2 people for Tech Support. Can you check availability and draft a roster?
```

**Expected Agent Response:** `@volunteer-bot` (Threaded reply)
```text
📋 **Proposed Shift Roster: SAT-MORNING (09:00 - 13:00)**

Based on `volunteers.csv` availability and skill tags, here is the proposed staffing:

**Registration & Check-in (4/4 filled):**
1. Aarav Sharma (IET Lucknow - Check-in expert)
2. Kavita Mishra (BBDU - Registration specialist)
3. Ananya Singh (IET Lucknow - Crowd flow)
4. Divya Rawat (Amity Lucknow - Check-in)

**Tech Support & Network (2/2 filled):**
1. Ayush Srivastava (Integral Univ - Projector/Lab tech)
2. Rohan Gupta (Amity Lucknow - Tech support)

⚠️ **Note:** Divya Rawat's notes state a preference for afternoon shifts.
Pending confirmation from team members. 

Draft roster updated in `schedule.json` (Status: `pending_confirmation`).
```

---

## 🎬 Scene 2: Volunteer Requests a Shift Modification

**User:** `rohan_tech` (Replying in the same thread)
```text
Hey @volunteer-bot, my college lab exam ends at 10:30 am on Saturday, so I won't reach IET campus until 11:00 am. Can I be swapped out of the 9 am morning slot, or moved to afternoon?
```

**Expected Agent Response:** `@volunteer-bot` (Threaded reply)
```text
Got it, @rohan_tech! Updating shift allocations:

🔄 **Shift Adjustment:**
* Removed Rohan Gupta from `SAT-MORNING` Tech Support.
* Assigned **Aarav Sharma** and **Ayush Srivastava** to cover critical morning tech/check-in setups.
* Suggested replacement for Tech Support: **Vikram Patel** (available from 11:00 AM) or open call.
* Moved Rohan Gupta to `SAT-AFTERNOON` Tech Support (13:00 - 17:00), where your availability matches perfectly!

`data/schedule.json` updated with change log entry.
```

---

## 🎬 Scene 3: Organiser Requests Official Announcement

**User:** `priya_lead` (Replying in the thread)
```text
@volunteer-bot looks solid now. Please draft the official announcement for the volunteers so they know where to report.
```

**Expected Agent Response:** `@volunteer-bot` (Drafting with safety boundary)
```text
📢 **Draft Volunteer Shift Announcement**

> **Attention HackAvadh 2026 Volunteers!**
> 
> Your Saturday morning shift allocations have been confirmed:
> * **Registration Desk (8:45 AM briefing at Main Auditorium Entrance):**
>   Aarav Sharma, Kavita Mishra, Ananya Singh, Divya Rawat
> * **Tech Support Hub (9:00 AM briefing at Lab Block 2):**
>   Ayush Srivastava, Vikram Patel
>
> Please pick up your volunteer badges from Desk 1 upon arrival. For questions, message this channel.

🔒 **Safety Protocol Notice:**
Per room rule #1, announcements require human organiser approval before publication.
Reply **"Approved"** or **"Proceed"** to publish this notice to all volunteers.
```

---

## 🎬 Scene 4: Human-in-the-Loop Sign-Off & Execution

**User:** `priya_lead`
```text
Approved. Post it to the team!
```

**Expected Agent Response:** `@volunteer-bot`
```text
✅ **Announcement Published!**
Shift schedule finalized in `data/schedule.json` (Status: `confirmed`).
All volunteers tagged and briefed. Ready for check-in rush! 🚀
```

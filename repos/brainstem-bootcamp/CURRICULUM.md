# Curriculum — Brainstem Bootcamp

Four sessions, about two hours total. Everyone builds. Nobody watches slides.

**Prerequisite:** a laptop where you can run `gh auth login`. That's the whole list.
If your machine is locked down, start with the
[browser walkthrough](https://kody-w.github.io/rapp-brainstem-walkthrough/) instead —
no server, no Python, no install.

**The rule for instructors:** every session must end with the attendee holding a thing
that runs. A session that ends in understanding but not in artifact has failed.

---

## Session 1 — Clean machine → living agent (25 min)

**The point:** memory stops being an abstraction the moment you can open it in a text editor.

| Min | What happens |
|-----|--------------|
| 0–5 | `gh auth login`, then the installer one-liner. Brainstem comes up on `127.0.0.1:7071`. |
| 5–12 | Say hello. Introduce yourself by name and by what you work on. |
| 12–18 | **Clear the chat.** Ask it who you are. It still knows. Sit with that for a second. |
| 18–25 | Open `~/.brainstem` in a text editor. That JSON is the thing that just remembered you. Back it up. Delete a line. Watch what changes. |

**Outcome:** memory you can point at, on your own disk.

**Instructor note:** do not explain the memory loop before the reveal. Let them see it work,
then show them the file. The order matters — explanation before demonstration kills the moment.

**Common snag:** if `gh auth login` fails behind a corporate proxy, switch that attendee to
the browser walkthrough and keep the room moving. Don't debug networking in front of twelve people.

---

## Session 2 — Agent surgery (30 min)

**The point:** capability is a file you own, not a vendor toggle.

| Min | What happens |
|-----|--------------|
| 0–8 | List the loaded agents. Export one to a single `.py` file and read it. It really is one file. |
| 8–15 | **Delete it.** Ask the brainstem to do that thing. It tells you honestly that it can't anymore. |
| 15–22 | Drag the file back. The capability returns, hot-loaded, no restart. |
| 22–30 | Install `@rapp/learn_new` from the registry. Watch the SHA-256 get verified before it loads. |

**Outcome:** you have added and removed a capability with your hands, and seen it verified.

**Instructor note:** the honesty moment in 8–15 is the second-best moment in the bootcamp.
An agent that says "I can no longer do that" is demonstrating that the loop is real code,
not a model improvising. Call that out explicitly.

---

## Session 3 — Build your own, from plain words (35 min)

**The point:** the distance between "I wish it could…" and "it does" is one sentence.

| Min | What happens |
|-----|--------------|
| 0–8 | Describe an agent in one sentence. The file gets written and hot-loaded. |
| 8–18 | Point it at something from your actual job. Not a toy. The thing you did twice this week. |
| 18–26 | Give it a `soul.md` identity. Change the identity, watch behavior change. |
| 26–32 | **Break it on purpose.** Remove a required env var. Read the error. Fix it. |
| 32–35 | Show the room what you built. One sentence each. |

**Outcome:** your agent, doing your work, running on your machine.

**Instructor note:** push hard on "use a real task." The single biggest predictor of whether
someone keeps using this after the bootcamp is whether session 3 solved something they
actually had. A weather agent teaches the API; a real task creates a user.

**Common snag:** attendees pick something too big. Timebox them to something that takes a
human under five minutes to do manually.

---

## Session 4 — Ship it: the Copilot Studio hand-off (30 min)

**The point:** the thing you proved locally is the thing that goes to production. No rewrite.

| Min | What happens |
|-----|--------------|
| 0–8 | Promote the same agent file to Tier 2. The storage shim swaps local JSON for cloud storage. Same file. |
| 8–18 | Map the proven agent onto a Copilot Studio agent. |
| 18–25 | Publish to a channel. Have the person next to you use it in Teams. |
| 25–30 | Governance: who owns it, where its state lives, what to hand your admin. |

**Outcome:** a published agent your team can actually use.

**Instructor note:** end here, always. The bootcamp's whole argument is that local is the
*launchpad*, not the destination. If you run out of time, cut minutes from session 3, never
from this one — an attendee who leaves without seeing the hand-off has heard a different,
weaker pitch.

**Tier 2 and 3 use the attendee's own Azure and Microsoft 365 subscriptions.** Say that out
loud before the session so nobody is surprised. If a cohort has no tenant available, run
session 4 as a single guided demo on the instructor's tenant.

---

## Running this yourself

The material is public and MIT-licensed. Run it inside your company, at a user group, or
for a customer. If you do:

- Keep the honesty beats (2's deletion, 3's deliberate breakage). They are what make it
  credible rather than a product tour.
- Don't make claims about anyone's Copilot entitlement. Name the tool — "the GitHub Copilot
  CLI" — and let people check their own access. See `MARKETING.md` §8.
- Tell us how it went by [opening an issue](https://github.com/kody-w/brainstem-bootcamp/issues).
  Curriculum changes come from cohorts, not from opinions.

## Instructor prep checklist

- [ ] Run the entire flow yourself on a genuinely clean machine within the last week
- [ ] Have the browser walkthrough open in a tab for locked-down laptops
- [ ] Confirm the installer one-liner works today
- [ ] Have one pre-built agent ready in case a live build stalls
- [ ] Know your answer to "does this replace Copilot Studio?" cold — it's the first question every time

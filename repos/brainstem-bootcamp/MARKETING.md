# Marketing plan — the next Brainstem Bootcamp

The short answer to *"what's the best way to market this?"*:

> **Stop marketing a bootcamp. Market a missing piece of the Microsoft AI platform,
> and make the bootcamp the two-hour way to get it.**

Nobody signs up for a bootcamp because they want a bootcamp. They sign up because
they have a problem they've already failed to solve twice. Sell the gap, sell the
hand-off, and let the cohort be the obvious next click.

---

## 1. The one-sentence position

**Brainstem is the on-device launchpad the Microsoft AI stack is missing — and Copilot
Studio is where what you build there lands.**

Three deliberate choices in that sentence:

- **"on-device launchpad"** — not a framework, not a competitor. A place things launch *from*.
- **"the Microsoft AI stack is missing"** — names the gap without attacking the platform.
  You're completing it, not replacing it. This is what makes the pitch survivable in
  a room full of Microsoft customers, partners, and employees.
- **"Copilot Studio is where it lands"** — the hero use case. Every demo ends there.
  This converts a threatened platform person into an ally, because your funnel feeds theirs.

**Never** position this as "better than Copilot." You lose the room, and it isn't true.
Copilot is excellent at the moment of the question. Brainstem is about the loop around it.

## 2. Who this is actually for

Ranked by conversion likelihood, not market size.

| # | Who | The pain in their words | The line that lands |
|---|-----|------------------------|---------------------|
| 1 | **Microsoft partner / SI consultants** | "I rebuild the same demo for every customer and can't show anything between the idea and a deployed Studio agent." | Same file, three tiers — prototype in front of the customer, publish after the meeting. |
| 2 | **Enterprise devs told to "add AI"** | "I have a prompt file and a hope. My prototype dies at the deployment step." | The rewrite between prototype and production is where your project dies. Delete the rewrite. |
| 3 | **Copilot Studio makers hitting a wall** | "I can publish, but I can't iterate or test locally, and I can't see why it did that." | Build and prove it on your laptop, then publish what already worked. |
| 4 | **Regulated-industry architects** | "I can't answer 'where does the AI's memory live?' in a review." | `~/.brainstem`. It's a filesystem answer, which is the answer compliance wants. |
| 5 | **Local-first / indie devs** | "I don't want another API key or another SaaS bill." | Nothing new to provision. It runs on the developer tooling you already sign into. |

Everything below targets #1 and #2 first. They have budget, urgency, and an audience.

## 3. The message ladder

Use the rung that matches how much attention you've actually earned.

- **3 seconds (social, conference badge, repo tagline)**
  *"Build the agent on your laptop. Ship it to Copilot Studio."*

- **30 seconds (a reply, a hallway, a comment thread)**
  *"Copilot answers questions. Copilot Studio publishes agents. Neither one gives you
  the place in between — where the agent gets built, remembers things, and gets proven
  before anyone depends on it. That's a local runtime, it's called Brainstem, and it
  takes one install line."*

- **3 minutes (a demo)**
  Don't explain. Do the memory trick: introduce yourself, clear the chat, watch it still
  know you — then open `~/.brainstem` in a text editor and show them the JSON. The moment
  someone sees their AI's memory as a file they could email, the abstraction collapses
  and the pitch is over. You've won.

- **30 minutes (the bootcamp)**
  They leave with a running agent published to a channel.

## 4. The demo that does the selling

One demo. Four beats. Under four minutes. It *is* the marketing — every channel below
is just a different frame around this clip.

1. **The install** — `gh auth login`, one curl line, brainstem is listening. No keys.
2. **The memory** — introduce yourself. Clear the chat. It still knows you.
   Open `~/.brainstem` and show the JSON on disk. *(This is the money shot.)*
3. **The surgery** — delete an agent file live; ask for that capability; it honestly says
   it can't anymore. Drag the file back; the capability returns. Capability is a file you own.
4. **The landing** — the same file goes to Copilot Studio, published, in Teams.
   *"That's the part your platform team already knows how to govern."*

Film it once, properly. Cut it four ways: 45s vertical hook (beat 2 only), 90s
(beats 1–2), 3min full, and a 12-min "with commentary" for YouTube/internal brownbags.

## 5. Channels, in priority order

**Tier 1 — where the buyers already are**

- **Microsoft partner and MVP communities.** The "I rebuild this demo every week"
  pain is universal there and these people have audiences of their own. One consultant
  who adopts this brings their next five customers.
- **Copilot Studio maker communities and user groups.** Lead with the hand-off, never
  the comparison. You are upstream of their tool, not competing with it.
- **Internal Microsoft field / SE channels**, if reachable. Frame strictly as
  "pipeline into Studio." Note the compliance rule in §8 before writing a word here.

**Tier 2 — reach**

- **A written technical post with the six pillars**, each one a claim you can verify on
  your own filesystem in under a minute. Ship it with the demo video embedded at beat 2.
- **Hacker News / r/LocalLLaMA / r/MSP** — HN title angle: *"Where does your AI agent's
  memory actually live?"* Lead with the filesystem answer, not the bootcamp. The bootcamp
  is the last line of the post, never the headline.
- **Conference lightning talks.** The 4-minute demo *is* a lightning talk already.

**Tier 3 — compounding**

- **The walkthrough as the top of funnel.** [The browser walkthrough](https://kody-w.github.io/rapp-brainstem-walkthrough/)
  needs no install, so it converts the "my laptop is locked down" crowd who would
  otherwise bounce. Every post links there first, the bootcamp second.
- **The public metrics dashboard** at [kody-w.github.io/RAR/metrics.html](https://kody-w.github.io/RAR/metrics.html)
  as social proof. Real downloads, real reviews, publicly auditable. Growth-in-the-open
  is itself a content series: post the number monthly.

## 6. Three-week launch sequence

**Week −1 — build the artifact**
- Film and cut the 4-minute demo.
- Publish this landing page (done) and get five people through the browser walkthrough.
  Watch where they hesitate; fix that copy before spending any reach.
- Line up **three named alumni outcomes**. Three real sentences from real people beat
  any amount of positioning.

**Week 1 — seed**
- Technical post + demo video into partner/MVP and Studio-maker communities.
- Personally invite 10 tier-1 ICPs to the first cohort. Not a broadcast — ten messages,
  each naming the specific thing that person has complained about publicly.
- Target: **12 seats claimed, 8 attend.** Small and finished beats large and drifting.

**Week 2 — run it and film it**
- Run the cohort. Record it (with consent). The recording becomes evergreen curriculum.
- Capture the artifact each attendee built. Ask one question at the end:
  *"What did you build, and what did it replace?"* That answer is next week's marketing.

**Week 3 — compound**
- Publish the alumni outcomes + the cohort recording.
- Open the next cohort with a waitlist. Waitlists convert better than open enrollment.
- Pitch the first **private team cohort** to whichever attendee was most enthusiastic.
  Team cohorts are the real distribution: one seat becomes twelve.

## 7. The objection table

Rehearse these. Each answer concedes something real first — that's why they work.

| Objection | Answer |
|-----------|--------|
| "Isn't this just Copilot with extra steps?" | Copilot answers. This is the loop around the answer — memory that always runs, agents you can delete, and a path to production. Different layer, not a competitor. |
| "We already have Copilot Studio." | Good — that's where this lands. This is the part before it: where you build and prove the agent so what you publish is something you've watched work. |
| "Custom instructions do this." | Instructions ask. A loop is code that runs whether the model cooperates or not. Also: instructions vanish outside the repo; this works with no repo at all. |
| "Local-only doesn't scale." | Correct, and it isn't meant to. Tier 1 is the workshop. Tier 2 is Azure. Tier 3 is Teams. Same file. |
| "IT won't let me install anything." | Then start in the browser walkthrough — no server, no Python, no install — and make the internal case with something you've already run. |
| "Who maintains this?" | It's MIT, public, and the registry metrics are published. Nothing is hidden behind a slide. |

## 8. Compliance rules — non-negotiable

Read before writing a single line of copy.

1. **Never make claims about anyone's Copilot entitlement.** Do not write "unlimited",
   "infinite", "free tokens", or anything implying what a subscription includes.
   The approved framing is: *"the GitHub Copilot CLI is the preferred backend"* — name
   the tool, never the entitlement. Whatever access a user has is between them and GitHub.
2. **No implied affiliation or endorsement.** Trademark and disclaimer language appears
   in the page footer and README, and stays there.
3. **"Free" refers to the bootcamp and this open-source project only** — never to a
   third-party service's usage.
4. **Don't disparage the platform.** "Missing piece" is the frame. "Broken" is not.
   The entire strategy depends on platform people seeing you as a feeder, not a threat.

## 9. What to measure

Vanity metrics are a trap here; the funnel is small and high-intent by design.

| Stage | Metric | First-cohort target |
|-------|--------|--------------------|
| Reach | Walkthrough starts | 200 |
| Interest | Walkthrough **completions** (14/14 steps) | 60 |
| Intent | Signup issues opened | 20 |
| Conversion | Attended | 8 |
| **Activation** | **Finished with a running agent** | **6** |
| Compounding | Alumni who bring a team cohort | 1 |
| Ecosystem | Registry downloads month over month | up and to the right |

The number that actually matters is **activation** — people holding a thing that runs.
Everything else is a leading indicator of it. If activation is high and reach is low,
spend on reach. If reach is high and activation is low, the curriculum is wrong,
not the marketing.

---

*Living document. If a cohort teaches us something, it gets edited here.*

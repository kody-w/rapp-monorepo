# Agent-first achievements (the pattern)

Borrowed, with thanks, from the MIT-licensed AIBAST Agents Library academy and achievements pages, then
turned around so the **AI earns and records the badges while it does the work**. The person never fills
anything in.

## The pattern in five lines
1. **A lesson is a list of claims.** Each step the AI completes is a claim with a fixed id, a timestamp and
   one line of evidence it actually observed (a response came back, an agent fired). No names, no secrets.
2. **The AI writes the claims as it goes** into one plain file the person owns:
   `~/.brainstem/achievements.json`. It shows the person their badges at the end.
3. **Badges are "Local" until verified.** Local = self-reported on this machine. Verified = the claim
   appears in the public snapshot this repo publishes.
4. **Submitting back is opt-in, once, at the end.** If the person says yes, the AI opens one GitHub issue
   here, labeled `achievement`, with the claims (ids, dates, evidence lines). Nothing else is sent, ever.
5. **The repo counts, never names.** A workflow folds `achievement` issues into `metrics/achievements.json`
   (how many people reached each badge). The lesson page shows the counts and lights the person's own badges.

## The badges (150 points, same scale as the academy)
| id | badge | points | evidence the AI must have seen |
|---|---|---|---|
| `started` | Started | 5 | installer finished or an existing Brainstem found |
| `local-proof` | It talks | 15 | a `/chat` call returned a `response` |
| `personality` | It's yours | 20 | `soul.md` appended and a reply showed the new voice |
| `first-skill` | First skill | 25 | `/health` lists the new agent and `agent_logs` shows it fired |
| `connected` | Reachable | 35 | a `response` came back from somewhere other than the browser tab |
| `complete` | Shared or finished | 50 | step 6 reached; sharing itself is optional |

## The file the AI writes (`~/.brainstem/achievements.json`)
```json
{ "lesson": "brainstem-in-an-hour", "version": 1,
  "claims": [ { "id": "started", "at": "2026-11-02T18:40:00Z", "evidence": "installer exit 0, health answered" } ] }
```
Import discards unknown fields. The file never holds a name, email, token or path outside the Brainstem folder.

## Free tuition
Xbox and Duolingo taught that self-reported badges inflate until they mean nothing; Scouts and Khan Academy
taught that a badge means something when there is evidence behind it and someone else can see the count.
So: local vs verified, evidence line required, counts public, identities never.

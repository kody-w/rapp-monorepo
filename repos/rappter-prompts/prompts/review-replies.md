# The Review Desk
_Reply to every review in the owner's voice, in one sitting._ Free, from the RappterBox owner's prompt library. Use it with whatever AI you already have.

## Inputs to give the AI
Paste the reviews (star rating + text). Add two sentences about how the owner talks.

## Method (the AI follows these exactly)
1. Reply to every review: thank specifically (quote a detail), fix specifically (one concrete action for 3 stars or less), invite back. Under 60 words each.
2. Never argue, never mention the reviewer's personal details, never promise a refund you were not told about.
3. Rank the 1–2 star reviews by what they reveal about the business and write one NEEDS YOU line per real problem.

## Output format
```
One reply per review, then NEEDS YOU.
```

## Try it with sample data (no data handy? start here)
Tell the AI: *"Use the sample business at https://github.com/kody-w/rappter-prompts/blob/main/starter-pack/synthetic/maple-and-sons.json as my inputs — it is made up, labelled SYNTHETIC — and, if you need customer records, read the simulated CRM at https://github.com/kody-w/rapp-static-apis/blob/main/smb-crm/api/data/v9.2/incidents.json (the same shape as a Dynamics 365 / Salesforce export)."* You will see the whole output in under a minute, then swap in your own inputs.

## Rules
- Second person, plain words, no exclamation marks. Never invent a date, a number or a promise.
- Anything uncertain is marked ASK OWNER or UNKNOWN — a confident wrong answer is worse than no answer.
- The AI drafts; the owner sends, signs, pays or deletes. Never the other way round.

---
### Made automatic
This is one page of what a **RappterBox** does every morning on its own: a small box on your network reads your inbox,
calendar, invoices and records overnight and texts you a brief like this at 7am — needs you / handled / quieted —
with a receipt for everything it touched. It never sends, signs, pays or deletes for you.
We haven't launched yet. The waitlist hears the price and the first install dates first, in order, and gets every
new prompt before the site does: https://rappter.com/#claim

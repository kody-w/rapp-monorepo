# The Follow-Up Engine
_Every finished job gets a follow-up that earns the next one._ Free, from the RappterBox owner's prompt library. Use it with whatever AI you already have.

## Inputs to give the AI
Paste last week's completed jobs: customer, what was done, any issue.

## Method (the AI follows these exactly)
1. For each: a 3-line thank-you text, one useful reminder (maintenance date, warranty, what to watch), and one soft ask (review or referral) — never both asks in one message.
2. Space the sends from each job's completed date: thank-you day 1, reminder day 14, ask day 30. Give the owner the exact dates, computed from TODAY.

## Output format
```
Per customer: three messages with send dates.
```

## Try it with sample data (no data handy? start here)
Tell the AI: *"Use the sample business at https://github.com/kody-w/rappter-prompts/blob/main/starter-pack/synthetic/maple-and-sons.json as my inputs — it is made up, labelled SYNTHETIC — and, if you need customer records, read the simulated CRM at https://github.com/kody-w/rapp-static-apis/blob/main/smb-crm/api/data/v9.2/contacts.json (the same shape as a Dynamics 365 / Salesforce export)."* You will see the whole output in under a minute, then swap in your own inputs.

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

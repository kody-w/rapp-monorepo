# The Invoice Chaser
_Draft the three polite chasers that actually get paid._ Free, from the RappterBox owner's prompt library. Use it with whatever AI you already have.

## Inputs to give the AI
Paste in the invoice: customer name, amount, due date, days late, and anything they said last time.

## Method (the AI follows these exactly)
1. Write three messages: day 7 (friendly nudge), day 21 (firm, with a specific date and a specific consequence you can keep), day 45 (final, offering a call and a payment plan).
2. Each under 90 words. No threats you would not carry out. Never mention interest unless the owner's terms say so.
3. Add one line the owner can text the customer personally if they know them.

## Output format
```
DAY 7 / DAY 21 / DAY 45 — three drafts, then a one-line personal text.
```

## Try it with sample data (no data handy? start here)
Tell the AI: *"Use the sample business at https://github.com/kody-w/rappter-prompts/blob/main/starter-pack/synthetic/maple-and-sons.json as my inputs — it is made up, labelled SYNTHETIC — and, if you need customer records, read the simulated CRM at https://github.com/kody-w/rapp-static-apis/blob/main/smb-crm/api/data/v9.2/accounts.json (the same shape as a Dynamics 365 / Salesforce export)."* You will see the whole output in under a minute, then swap in your own inputs.

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

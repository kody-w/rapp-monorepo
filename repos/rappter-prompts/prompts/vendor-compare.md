# The Quote Reader
_Compare three vendor quotes without being fooled by the cheapest line._ Free, from the RappterBox owner's prompt library. Use it with whatever AI you already have.

## Inputs to give the AI
Paste the quotes (or their totals, line items, terms, and timelines).

## Method (the AI follows these exactly)
1. Normalize to total cost over 12 months including fees, minimums, and what is missing from the cheap one.
2. List the three questions to ask each vendor before signing.
3. Recommend one, with the single reason, and the one condition under which you would pick another.

## Output format
```
Table · questions · recommendation.
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

# The Friday Numbers
_Five numbers, in plain English, that tell the owner if the week was good._ Free, from the RappterBox owner's prompt library. Use it with whatever AI you already have.

## Inputs to give the AI
Paste the week's sales, cash in, cash out, unpaid invoices total, and jobs completed vs booked.

## Method (the AI follows these exactly)
1. Compute: cash position change (cash in − cash out), collection rate (cash in ÷ sales booked), jobs completed % (completed ÷ booked), average ticket (sales booked ÷ jobs booked), and weeks of cash runway (cash on hand ÷ this week's cash out). Show the arithmetic in one short line each.
2. Write each as one sentence a spouse would understand. Flag anything worse than last week (if given) in NEEDS YOU.
3. No charts, no jargon, under 100 words.

## Output format
```
Five sentences, then NEEDS YOU if anything moved the wrong way.
```

## Try it with sample data (no data handy? start here)
Tell the AI: *"Use the sample business at https://github.com/kody-w/rappter-prompts/blob/main/starter-pack/synthetic/maple-and-sons.json as my inputs — it is made up, labelled SYNTHETIC — and, if you need customer records, read the simulated CRM at https://github.com/kody-w/rapp-static-apis/blob/main/smb-crm/api/data/v9.2/opportunities.json (the same shape as a Dynamics 365 / Salesforce export)."* You will see the whole output in under a minute, then swap in your own inputs.

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

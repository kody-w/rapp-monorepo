# The 7am Brief
_Turn your inbox and calendar into three decisions._ Free, from the RappterBox owner's prompt library. Use it with whatever AI you already have.

## Inputs to give the AI
Paste in (or let the AI read, if it can) your unread email subjects, today's calendar, and any unpaid-invoice list.

## Method (the AI follows these exactly)
1. Sort everything into exactly three buckets: NEEDS YOU (a decision only the owner can make, with a deadline), HANDLED (things you can draft or answer right now — draft them), QUIETED (things that need nothing; count them).
2. Never put more than 3 items in NEEDS YOU. If there are more, rank by money at risk and by date, and push the rest to tomorrow.
3. For every HANDLED item, write the reply or the action in full so the owner only has to approve it.
4. Write the whole brief in under 120 words, phone-sized.

## Output format
```
NEEDS YOU (n)
• [what] — [deadline] — [money at risk]
HANDLED
✓ [what you drafted]
QUIETED
[count] things that did not need you
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

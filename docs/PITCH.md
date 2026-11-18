# FoodLoop pitch sheet

Keep this open when you talk about the project. Numbers are sourced in `LIMITATIONS.md`. Nothing here claims results the prototype has not produced.

---

## At a glance

| | |
|---|---|
| **What** | A prototype that spots food about to spoil, proposes where it should go, requires a human decision, and records every step |
| **Status** | Working software prototype (open source). Trained on public photos. Not validated for food safety. No field trials. |
| **Origin** | First place, UFV Community Ideation Jam 2026, Future Ready Communities theme |
| **Built by** | Harshit, Bachelor of Computer Information Systems co-op student, University of the Fraser Valley |
| **Stack** | Python, FastAPI, SQLite, PyTorch (MobileNetV3-small), Jinja templates |
| **Code** | github.com/HarshitSaini0/foodloop (update once pushed) |

---

## The problem (with sources)

- Canada loses or wastes about **35.5 million tonnes** of food a year, **58%** of what it produces. **11.2 million tonnes** of that is avoidable, edible food. *(Second Harvest and VCMI, 2019)*
- A 2024 update puts unused food at **46.5%**, about **21.1 million tonnes**. *(Second Harvest, reported by CTV, 2024)*
- Meanwhile about **9.8 million people** in Canada lived in a food-insecure household in 2025, including about **2.4 million children**. *(PROOF, from Statistics Canada, 2025 data)*
- Worldwide, **1.05 billion tonnes** of food was wasted in 2022 and food loss and waste causes **8 to 10%** of greenhouse gas emissions. *(UNEP, 2024)*

The gap this targets: edible food is often thrown away because nobody can check it, route it and prove where it went fast enough.

## The solution

```
photo -> model proposes -> rules pick a route -> PERSON confirms or overrides
      -> donor confirms handover -> recipient confirms receipt -> credit logged
```

Three ideas make it different:

1. **People decide.** The model never has the last word. Risky foods and low confidence go to hold.
2. **Plain rules.** Routing follows the EPA Food Recovery Hierarchy and can be read in one file.
3. **A record you can check.** A hash-chained log shows if anyone edited history.

---

## Say it at three lengths

**10 seconds**
> FoodLoop proposes where food about to spoil should go, makes a person confirm it, and keeps a record anyone can check. It won first place at UFV's Community Ideation Jam, and I built a working prototype.

**30 seconds**
> Canada wastes about 46% of the food it produces, and a lot of it is still edible, while millions of people can't afford enough to eat. FoodLoop is a prototype that looks at a photo, proposes a route such as people first, then compost, and requires a human to confirm before anything moves. Every step goes into a tamper-evident log. It's trained on public photos and not validated for food safety, so the person stays in charge.

**60 seconds**
> Add: how it works (photo, model, rules, human review, donor and recipient confirmations, credit in the log), why rules and not an LLM make the decision, the false-safe rate as the metric that matters, and the next step (test with real photos and a food-safety professional).

---

## Tailor the opening

| Audience | Lead with | Then |
|---|---|---|
| Recruiter or hiring manager | What you built: FastAPI service, hash-chained ledger, PyTorch classifier, 12 tests, deployed on your own server (optional) | Design decisions: rules over LLM, human-in-the-loop, honest evaluation |
| Food bank or rescue organisation | The hold route and the human check | Ask what intake checks they already use and where a photo helps or does not |
| Farmer or grocer | Catching edible food earlier, a log that shows where it went | Ask what spoilage decisions they make by eye today |
| Professor or judge | Problem numbers, EPA hierarchy, limits | The evaluation plan and the false-safe rate |
| Investor or funder | Honest stage: prototype, no field data | The smallest next step: a supervised pilot with real photos |

---

## 90-second demo script

1. Open **Scan**. Upload a produce photo. Choose a category.
2. Show the result: label, confidence, **backend name**, suggested route and reason.
3. Switch the category to dairy and scan again: it goes to **hold** regardless of confidence.
4. Review as a named person. Override one route to show it is the person who decides.
5. Donor confirms, then recipient confirms. Show the credit appearing.
6. Open **Ledger**: chain intact. Say what a tamper would look like.
7. Say the limits out loud: public-photo model, not validated, demo credit.

## Hard questions, honest answers

| Question | Answer |
|---|---|
| How accurate is it? | I'll give you the number from the held-out test set and its false-safe rate. It's trained on public photos, so I don't claim it works on real batches yet. *(Fill in after running `evaluate.py`.)* |
| Why not use an LLM? | Routing needs to be predictable and auditable. Rules give the same answer every time and can be tested. |
| Is this blockchain? | No. It's a hash chain in SQLite. It shows edits to old records, nothing more. |
| Can the credits be gamed? | Yes in principle. Names aren't verified. That's listed as a limitation, with caps, audits and accounts as fixes. |
| Will it solve hunger? | No. Food insecurity is mostly an income problem. This could help move edible food faster. |
| Is it safe to donate food it approves? | Not on its own. Safety needs trained people and checks a photo can't do. The review step exists for that reason. |
| What did the award cover? | The idea at the UFV Community Ideation Jam 2026. The software was built afterward as a prototype. |
| What next? | Real photos from a partner site, a food-safety professional reviewing the rules, then a small supervised pilot. |

---

## Claims check (before you post or present)

- [ ] Any number has a source and year next to it
- [ ] "Prototype" and "not validated for food safety" appear
- [ ] No claim about waste reduced, food saved, or accuracy unless it comes from your own measured results
- [ ] "Hash chain" or "tamper-evident", never "blockchain" or "tamper-proof"
- [ ] The award is described exactly: first place, UFV Community Ideation Jam 2026

## Call to action

- Developers: read `docs/ARCHITECTURE.md` and try the code
- Food rescue and farm teams: tell me what a photo can and can't help you decide
- Everyone: if you spot a flaw in the design, open an issue

---

## LinkedIn post skeleton

> I won first place at UFV's Community Ideation Jam with an idea called FoodLoop. Then I built it.
>
> It's a prototype that looks at a photo of food, proposes where it should go (people first, then compost), and requires a person to confirm before anything moves. Every step is written to a tamper-evident log.
>
> What it is: Python, FastAPI, a small PyTorch model, a rule engine, a hash-chained ledger, 12 automated tests.
> What it isn't: validated for food safety. It's trained on public photos, so a person always decides.
>
> Canada wastes about 46% of the food it produces (Second Harvest, 2024) and the avoidable part could feed people. A faster, checkable handoff might help. I'd like to learn what real food rescue teams need.
>
> Code and docs: [link]
>
> #foodwaste #python #machinelearning #communitytech

*(Swap in your measured results and the repo link before posting.)*

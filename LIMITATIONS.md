# Limitations, accuracy, and the numbers

Read this before quoting FoodLoop anywhere. It separates what the prototype **does**, what it **does not prove**, and which numbers are real (with sources) versus assumptions.

## 1. What this prototype is

A working demonstration of a workflow: photo, proposal, rules, human check, handover confirmations, tamper-evident log. It is not a food-safety tool, not a deployed service, and has no users.

## 2. Why the model is not accurate enough to trust

These are the real reasons, not boilerplate.

1. **A photo shows the surface only.** Spoilage that matters for safety (bacteria, toxins, internal mould, temperature abuse) is mostly invisible. Looking fresh is not the same as being safe.
2. **Public datasets are easy.** Fresh-vs-rotten photo sets are usually clean, well lit, and shot against plain backgrounds. A model can score very high on them and still fail in a crate, a dim storeroom or a farm field. A high test score on a public set says little about real use. (This is a general machine-learning caution, not a measured result for this repo.)
3. **Only two classes.** The model says `fresh` or `rotten`. Real food has many states in between, and many kinds of food it has never seen.
4. **It will be confidently wrong sometimes.** Confidence scores from small image models are not reliable probabilities. The 0.80 floor is a safety habit, not a calibrated guarantee.
5. **The placeholder is not a model.** Without `model/model.pt`, the app uses a colour-counting heuristic. It is labelled `demo-heuristic` on every result and exists only so the workflow runs.
6. **No real-world validation.** Nobody has compared its calls against a trained food-safety inspector on real batches.

**The number that matters most is the false-safe rate:** rotten food predicted fresh, divided by all rotten food. `model/evaluate.py` computes it on a held-out test folder. Until you run it, **this repo has no accuracy figure and none should be claimed.**

## 3. Where the design can still fail

| Weak point | Why it matters | Possible fix (not built) |
|---|---|---|
| Humans can rubber-stamp | Mandatory review only helps if reviewers actually look | Show the model's reasons, require a second check for risky categories, audit override rates |
| Names are free text | "Donor" and "recipient" are just strings, so two colluding or fake parties could trigger a credit | Real accounts and verified organisations |
| Ledger proves edits, not events | A hash chain shows records were not altered later. It cannot show the food was really handed over. | Signed receipts, recipient-side confirmation through a separate device, spot checks |
| Chain can be rebuilt by whoever owns the file | Someone with database access could recompute every hash | Publish the latest hash somewhere public on a schedule |
| Credits can be gamed | A credit for donated food could be farmed with staged batches | Caps, sampling audits, no money value until validated |
| Higher-risk foods | Meat, dairy and ready-to-eat food carry the worst safety risk | Held by rule. A person decides. |
| Photo is the only input | No temperature, time, storage or batch history | Sensors and records (future work) |
| Single shared password, no roles | Fine for a demo, not for real use | Proper authentication |
| Privacy | Photos could contain people or private places | Demo photos only. Do not upload anything else. |

## 4. What food rescue does and does not fix

Food rescue and diversion is worthwhile, but it does not solve hunger on its own. PROOF, the Canadian food-insecurity research group at the University of Toronto, publishes the point that food insecurity is mainly a problem of inadequate income, so donated food is not a complete answer. FoodLoop should be described as a way to **waste less edible food and move it faster**, not as a solution to food insecurity.

## 5. Numbers you can use

All checked on 2026-11-18. Each is from the source named. Quote them with the source and the year.

### Canada: food waste

| Figure | Source and notes |
|---|---|
| 35.5 million tonnes of food lost and wasted a year, which is 58% of food produced, worth about $49 billion | Second Harvest and Value Chain Management International, *The Avoidable Crisis of Food Waste* (2019). https://secondharvest.ca/research |
| Of that, 11.2 million tonnes (32%) is **avoidable and edible**, food that could be redirected to people | Same report |
| Update: 46.5% of food produced in Canada, about 21.1 million tonnes, is never used | Second Harvest and VCMI update, reported by CTV News (Oct 2024). https://calgary.ctvnews.ca/nearly-half-of-the-food-produced-in-canada-is-wasted-annually-report-1.7083194 |
| Avoidable food waste contributes about 25.7 million tonnes of CO2 emissions a year | Same update, reported by CTV News |
| Overall waste fell about 20% since 2019, but the avoidable part rose about 6.5% | Same update, reported by CTV News (https://www.ctvnews.ca/toronto/article/almost-half-of-all-food-wasted-in-canada-is-avoidable-new-report-suggests/) |

Caution: the two reports use different definitions and methods, so do not subtract one from the other as a trend. Press coverage of the 2024 update gives the dollar value of avoidable waste in more than one way, so this sheet leaves that dollar figure out.

### World

| Figure | Source and notes |
|---|---|
| 1.05 billion tonnes of food wasted in 2022, about 132 kg per person, almost one fifth of food available to consumers | UNEP Food Waste Index Report 2024. https://wedocs.unep.org/bitstream/handle/20.500.11822/45275/Food-Waste-Index-2024-key-messages.pdf |
| Households 631 million tonnes (about 60%), food service 290 million, retail 131 million | Same report |
| Food loss and waste generates 8 to 10% of global greenhouse gas emissions | Same report |
| 783 million people hungry while this happens | Same report |

### Canada: food insecurity

| Figure | Source and notes |
|---|---|
| 2025 data: 24.0% of people nationally, about 9.8 million, lived in a food-insecure household, down from 25.7% in 2024. About 2.4 million children (30.8%). | PROOF analysis of Statistics Canada's Canadian Income Survey. https://proof.utoronto.ca/?p=8132 |
| Previous release (ten provinces only): 25.5%, about 10 million people including 2.5 million children, a record high | PROOF. https://proof.utoronto.ca/?p=7817 |

Caution: the newer release now includes the territories, and the survey year labels are confusing (a 2024-labelled dataset mostly reflects early 2025). Do not mix the two series.

### Framework

| Fact | Source |
|---|---|
| The EPA Food Recovery Hierarchy ranks actions from most to least preferred: source reduction, feed hungry people, feed animals, industrial uses, composting, then landfill or incineration | U.S. EPA. https://www.epa.gov/sustainable-management-food/food-recovery-hierarchy |

### Numbers that are not here on purpose

- **Anything about FoodLoop's accuracy.** None exists yet. After you run `evaluate.py`, add the real table to `README.md`.
- **Tonnes saved, dollars saved, emissions avoided by FoodLoop.** The prototype has saved nothing. Any scenario figure in the research paper (for example a share of avoidable waste redirected) is an **assumption for illustration**. Label it that way every time, and keep it out of the code and README claims.

## 6. Wording guide

| Say | Do not say |
|---|---|
| "A prototype that proposes a route and requires a human decision" | "AI that detects spoiled food" |
| "Trained on public photos, not validated for food safety" | "Accurate", "reliable", "safe" |
| "Tamper-evident record" | "Blockchain", "tamper-proof", "trustless" |
| "Won first place at the UFV Community Ideation Jam 2026 (Future Ready Communities)" | "Award-winning product" |
| "Could help move edible food to people faster" | "Reduces food waste by X%" |
| "Demo credit, no monetary value" | "Carbon credit", "tokens" |

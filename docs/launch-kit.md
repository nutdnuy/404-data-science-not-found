# Launch kit

Use this copy after checking the repository URL and running the documented example. The language below describes the initial scope; it does not claim adoption, benchmark scores, or improved business outcomes.

## Positioning

**One line:** Composable AI agent skills for data science, from a business question to a reviewable result.

**Problem:** An agent can produce a plausible notebook before anyone has agreed on the decision, the prediction time, or what evidence would make the answer useful.

**Approach:** Twelve focused skills create explicit handoffs between requirements, analysis, preparation, modeling, evaluation, inference, and reporting. A leakage audit and a coordinating pipeline connect the stages. Each stage should leave artifacts a person can inspect.

**Initial proof:** A runnable example using synthetic subscription data, plus proposed evaluation scenarios. Synthetic results demonstrate the workflow; they are not evidence of real customer behavior or production readiness.

## English launch post

I’m building **404 Data Science Not Found**: 12 composable skills for AI coding agents that take a data project from requirements to a reviewable report.

The question I want an agent to answer before “which model?” is: **What decision are we making, and what data would actually be available then?**

The collection covers requirements, solution design, EDA, cleaning, insights, feature engineering, model development, evaluation, inference, reporting, leakage auditing, and a coordinating pipeline.

The repository includes a runnable synthetic subscription-retention example and eight proposed evaluation scenarios, including future-data leakage, repeated customers, holdout reuse, and instructions hidden in a data field.

Install:

```sh
npx skills add nutdnuy/404-data-science-not-found
```

I’d like feedback from people doing real analysis: **which handoff between these stages costs you the most rework?** A small reproducible example of where a skill fails is especially useful.

Repository: https://github.com/nutdnuy/404-data-science-not-found

## Thai launch post

ผมกำลังทำ **404 Data Science Not Found** ชุด 12 สกิลสำหรับ AI coding agent ให้ทำงานตั้งแต่เก็บความต้องการจนถึงรายงานที่คนตรวจสอบต่อได้

ก่อนถามว่า “ใช้โมเดลอะไรดี” ผมอยากให้ agent ตอบให้ได้ก่อนว่า **เรากำลังตัดสินใจเรื่องอะไร และในเวลาที่ตัดสินใจ เรามีข้อมูลอะไรอยู่จริงบ้าง?**

สกิลครอบคลุม requirements, solution design, EDA, data cleaning, insight, feature engineering, model development, evaluation, inference และ report พร้อม leakage audit และ pipeline สำหรับประสานแต่ละขั้น

ใน repo มีตัวอย่าง subscription retention ที่รันได้ด้วยข้อมูลสังเคราะห์ และโจทย์ประเมินที่เสนอไว้ 8 สถานการณ์ เช่น ข้อมูลอนาคตหลุดเข้าโมเดล ลูกค้าคนเดียวอยู่ทั้ง train/test การใช้ holdout ซ้ำ และคำสั่งที่ซ่อนอยู่ในช่องข้อมูล

ติดตั้งได้ด้วย:

```sh
npx skills add nutdnuy/404-data-science-not-found
```

อยากฟังจากคนทำ Data Science ครับว่า **รอยต่อระหว่างขั้นตอนไหนทำให้ต้องย้อนกลับไปแก้งานบ่อยที่สุด?** ถ้ามีตัวอย่างเล็ก ๆ ที่ทำให้สกิลทำงานพลาด เปิด issue มาได้เลยครับ

ตัวอย่างใช้ข้อมูลสังเคราะห์เพื่อสาธิตวิธีทำงาน ผลลัพธ์จึงยังไม่ได้ยืนยันว่าจะใช้ได้ดีกับข้อมูลธุรกิจจริง

Repository: https://github.com/nutdnuy/404-data-science-not-found

## Short version

**English:** Before an AI agent picks a model, make it define the decision, the prediction time, and the evidence. 404 Data Science Not Found is a collection of 12 composable skills with a runnable synthetic example. Which data-science handoff would you improve first? https://github.com/nutdnuy/404-data-science-not-found

**ไทย:** ก่อนให้ AI เลือกโมเดล ให้มันอธิบายการตัดสินใจ เวลาที่ใช้ทำนาย และหลักฐานที่ต้องมีก่อน ผมทำ 404 Data Science Not Found ไว้ 12 สกิล พร้อมตัวอย่างข้อมูลสังเคราะห์ที่รันได้ ลองแล้วเจอขั้นตอนไหนควรปรับ บอกกันได้ครับ https://github.com/nutdnuy/404-data-science-not-found

## Demonstration outline

Record only after the example has completed successfully on the release revision. Keep the demo to about 90 seconds and show real files or terminal output; do not simulate a successful run.

1. **0–15 seconds:** Show the business question and the decision the example is intended to support.
2. **15–35 seconds:** Show how the workflow records prediction time and excludes unavailable information.
3. **35–65 seconds:** Run the example and open its actual artifacts. Explain one concrete finding and one limitation.
4. **65–90 seconds:** Show the skill entry points and invite a reproducible failure report. Link to the installation instructions and evaluation scenarios.

Do not turn synthetic model scores into a headline about business value. If the example fails, fix it before recording or show the failure and describe what remains unresolved.

## Fourteen-day distribution plan

This is a proposed owner-run plan, not a scheduled automation or permission to post to any channel. Choose communities where the topic fits and follow their self-promotion rules. One helpful conversation is more useful than repeated link drops.

| Day | Work | Reviewable output |
| --- | --- | --- |
| 1 | Run a clean installation and the example from the public release revision. | Record the revision, commands, environment, and observed result. Fix broken instructions. |
| 2 | Ask two willing practitioners to follow the quickstart without coaching. | List where they stopped, misunderstood an artifact, or needed missing context. |
| 3 | Improve the first-run experience using that feedback. | Small fixes and a changelog entry describing the actual change. |
| 4 | Record the demonstration above. | A short demo that shows a real run and one limitation. |
| 5 | Publish one launch post on the owner’s preferred channel. | A post using the English or Thai copy, with a direct repository link. |
| 6 | Respond to questions with concrete examples. | Issues for reproducible problems; documentation fixes for repeated confusion. |
| 7 | Review first-week feedback and choose one narrow improvement. | A public issue explaining the problem and acceptance criteria. |
| 8 | Share a short explanation of a leakage failure that uses synthetic data. | A useful technical example readers can inspect without installing the collection. |
| 9 | Invite an interested contributor to reproduce one evaluation scenario. | An evaluation record including the agent, version, prompt, and artifacts. |
| 10 | Improve the weakest observed handoff. | A focused pull request; avoid expanding scope to answer every feature request. |
| 11 | Share a before/after example of that improvement. | Real evidence from the same scenario, with remaining limits stated. |
| 12 | Participate in one relevant discussion where the workflow addresses an existing question. | An answer that stands on its own; disclose ownership if linking the repository. |
| 13 | Review installation friction, useful issues, and contributions. | A short maintainer note separating observed usage from guesses. |
| 14 | Publish a progress note and adjust the roadmap. | What shipped, what failed, what changed, and one specific contribution request. |

## What to measure

- **First-run success:** How many consenting testers completed the quickstart, out of how many who tried. Report the denominator and failure reasons.
- **Useful feedback:** Issues that contain a reproducible problem, a missing assumption, or a demonstrable documentation gap.
- **Evaluation evidence:** Completed scenario records with prompts and inspectable artifacts, including failures.
- **Community participation:** People who review, reproduce, or contribute a change. Count real contributions without inferring identities or collecting private data.
- **Reach:** Public views or stars may help describe discovery, but do not establish quality, adoption, or usefulness.

There is no guaranteed route to virality. Avoid purchased stars, engagement exchanges, fake testimonials, mass direct messages, or repeated promotional replies. Build the next release around evidence that someone could use the project successfully.

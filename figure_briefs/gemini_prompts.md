# ActDelta figure drafts for Gemini

These prompts are for visual ideation only. The selected drafts must be redrawn as editable SVG/PDF with verified labels before inclusion in the manuscript.

## Shared visual language

- ACM MobiCom systems-paper style, clean flat vector infographic, white background.
- Restrained palette: navy `#2F5597`, light blue `#DCE6F1`, muted green `#D9EAD3`, pale peach `#FCE4D6`, neutral gray `#E7E6E6`, warning red `#C94C4C`.
- Thin dark-gray outlines, straight orthogonal arrows, no gradients, no shadows, no photorealism, no decorative background.
- Designed to remain legible in a two-column paper at single-column width; large visual elements and very little text.
- Use Times-like typography if text is rendered. Do not invent numbers, equations, module names, or claims.
- Produce a 4:3 academic figure, isolated on a pure white canvas.

## Figure 1 — ActDelta closed-loop setting

Create a polished academic system-concept figure for a MobiCom paper about predictive uplink scheduling for an edge-offloaded robot policy.

Composition: a compact robot manipulation scene on the left, an edge server on the right, and the ActDelta scheduler between them. The robot has two camera streams: an "agent view" that may be transmitted or predicted, and a small wrist camera labelled "wrist view: always current". Show a blue wireless uplink carrying a real agent-view frame from the robot to the edge server only when predicted decision relevance is high. Inside the scheduler, show four compact stages in order: Encoder, World Model Rollout, Relevance Head, Budget Gate. When a frame is suppressed, show the world model advancing a predicted agent view with a dotted path. The edge server runs a frozen policy and returns an action chunk to the robot. The returned action also conditions the next world-model rollout, forming a clearly visible dashed closed loop.

Visual storytelling: emphasize the scheduling decision, not neural-network internals. Use blue for real transmissions and resets, gray dashed arrows for local prediction, green for action return, and a small red warning accent beside long open-loop age. Include only these short labels: Agent view, Wrist view always current, Encode, Predict, Score relevance, Budget gate, Send / Suppress, Frozen edge policy, Action chunk, Reset, Roll forward. Avoid equations and long sentences.

Reference style: AutoIOT Figure 1 from ACM MobiCom 2025 — a central mechanism surrounded by concrete application components and compact callouts — but adapt it to a robot/edge closed loop and do not copy its content.

## Figure 2 — Three objectives and the broken proxy chain

Create a conceptual academic figure explaining that three objectives are related but not interchangeable in predictive robot communication.

Use three large horizontal cards arranged from left to right. Card 1 is "Reconstruction fidelity" and visually compares a predicted camera frame with a true frame using a pixel/SSIM-style similarity icon. Card 2 is "Decision relevance" and shows two action trajectories or robot action chunks diverging when the true observation replaces the prediction. Card 3 is "Refresh value" and shows two episode outcomes, success versus failure, under send versus suppress decisions.

Between Card 1 and Card 2, show a thin broken or weak link labelled only "weak alignment"; make this a small muted-red break, not a dramatic failure. Between Card 2 and Card 3, show a larger open bridge or gap labelled "oracle still does not close the gap". Under the cards, add three compact evidence badges: "C1: decoupled", "C2: learnable offline", and "C3: not established online". The main message should be instantly visible: better prediction of per-frame action change does not guarantee better episode-level transmission scheduling.

Visual style: use neutral gray for fidelity, blue for decision relevance, and pale peach/red for refresh value. Use real robot/camera/action icons rather than abstract circles. Keep the hierarchy crisp and readable at single-column width. No charts, no axes, no 3D, no decorative illustration.

Reference style: the scenario-separated, pastel-panel visual grammar of PolarVisor Figure 2 (ACM MobiCom 2025), combined with the compact multi-scenario icon grammar of FedDC Figure 1 (ACM MobiCom 2025); do not copy either figure's technical content.

## Figure 3 — Frozen four-stage evaluation protocol

Create a clean academic evaluation-workflow figure for a MobiCom systems paper. Show four stages from left to right as four aligned modules connected by arrows:

1. Pilot — 500 pairs — choose the trigger metric.
2. Offline — 4,200 pairs — train and validate the relevance head.
3. Blind closed loop — 800 cells — freeze everything and compare rate-matched schedulers using predicted relevance.
4. Oracle closed loop — 400 cells — replace only predicted relevance with true action divergence.

Each stage must have a small concrete icon: paired camera frames for Pilot, a dataset plus lightweight head for Offline, a robot episode plus sealed result envelope for Blind, and an eye/oracle symbol replacing only one signal for Oracle. Put a closed padlock on every completed stage and a continuous bracket below all stages reading "freeze before advancing the claim". Make the one-variable substitution from Stage 3 to Stage 4 visually explicit: predicted relevance changes to true action divergence; policy, predictor, tasks, initial states, budgets, and statistics remain frozen.

Use a restrained left-to-right pipeline inspired by AutoIOT Figure 5 (ACM MobiCom 2025), but much simpler and suitable for a single-column figure. Use gray for Pilot, light blue for Offline, deeper blue for Blind, pale peach for Oracle, and red only for the single substituted signal. Keep all text large and concise. No background scenery, no unnecessary icons, no gradients, no shadows.


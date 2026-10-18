# Director evidence implementation plan

Goal: improve concept-to-shot decisions and make failures observable; verify with an original 36s film, not prompt length.
Architecture: retain Canvas 2D, seek(t), existing B/C appearance and all render commands. Add a short director contract, shot recipes and timestamped revision ledger; extend only proven missing utilities. No third-party rendering framework.
Spec: user task dated 2026-10-17; scope/decisions in audit.md.

## Constraints and experiment
- Preserve original 62d51508aad00003dc6209afa80c4b5dc540de59 in detached worktree.
- No supplied Opus reference file exists in /workspace; do not claim to have viewed it.
- No API credentials configured. Use two fresh same-session-model agents with same topic, 36s, Canvas, fonts, physics, maximum 20min creative budget and two image-led passes. No DeepSeek efficacy claim. Parent engine/docs work is additional development cost, explicitly excluded from generation budget.
- Baseline follows original Skill; upgraded arm follows new Skill. Neither sees the other's film. Agent nondeterminism and n=1 preclude causal/model-general claims.
- Topic: straight vs cycloid, x=1m, drop=.6m, g=9.81, frictionless particle from rest. Source: Wolfram MathWorld BrachistochroneProblem and Cycloid, fetched successfully.
- No watermark, no human voice, no public deployment; feature branch PR only.

## Tasks
1. Audit: read all source/references, inspect comparison JPG and old GIF frames; render old examples. Record external source commits/licenses and adopt/reject decisions.
2. Reliability: write failing tests for deterministic failure, swallowed events, failed encode, invalid time ranges, short audio fade. Fix only reproduced failures; preserve old behavior on valid input. Browser override via VK_BROWSER and bundled Chromium fallback enables cloud/Windows.
3. Director workflow: replace restrictive B/C-only and literal-only directives with concise decision workflow; add visual direction contract, concepts/shot/revision artifacts, rendering recipes and factual limitations. Keep historical analyses marked historical.
4. Original film: two independent fresh same-model arms, each outputs source, storyboard, facts, keyframes, motion strip and 36s video; inspect artifacts before revision. Freeze first pass, record reason and same-time after images. Shared deterministic physics is independently checked.
5. QA: add objective media probe (codec/rate/duration/audio/black/silence candidates), distinguish candidate diagnostics from aesthetics, automated negative fixtures, Windows recipe.
6. Verify: all tests; old examples --det + clips; final film --det + actual images + encoded streams/audio. Independent review, address substantive defects, publish reviewable artifacts in repo and create PR.

## Review focus
Failed encoder cleanup; out-of-order seeks after event export; clip rounding and empty clips; missing fonts and browser failures; no unsupported experimental/aesthetic claims.

## Ledger
- Original source read: 3,662 lines (excluding README/license/fonts). Original fold/pigeon contact sheets rendered using external browser launcher shim, unchanged engine. Upstream and fork HEAD identical.
- Original --det only prints failure; events catches all draw exceptions; ffmpeg exit ignored in serial path. Regression tests will confirm.
- Ruling: user authorized uninterrupted implementation and PR; no repeated design approval gates.
- Ruling: keep evidence under evidence/ instead of ignored review/renders. Include compact MP4s and full-resolution representative frames; raw lossless intermediates reproducible locally.

# Analysis & source materials

The discovery and design trail that produced this platform, preserved for traceability.

> ⚠️ **CONFIDENTIAL — contains client PII** (call recording/transcript, sample financial
> figures, DOB and last-4 SSN in sample data). Do not distribute. If this repo is ever pushed
> to a remote, review access controls first.

## Contents

- **`source/`** — the original inputs
  - `AW - AI Test Project.mp4` — the recorded discovery call
  - `PRD AI Engineer Test.pdf` — the product requirements document generated from the call
- **`AW_AI_Test_Project_Report.md`** — analysis of the video call
- **`PRD_AI_Engineer_Test_Report.md`** — analysis of the PRD
- **`Technical_Spec_AW_Client_Report_Portal.{md,docx,pdf}`** — the approved technical spec the
  build was implemented from
- **`AW_sample_SACS.pdf`, `AW_sample_TCC.pdf`** — sample report output from the portal
- **`working/`** — intermediate artifacts: extracted audio (`audio16k.wav`), the transcript
  (`transcript.txt/.srt`), extracted frames and figures, the PRD text extraction, and the
  build scripts used to produce the spec/PDFs (`node_modules` excluded — run `npm install`
  under `working/specbuild/` to regenerate)

## Note on large files

`source/AW - AI Test Project.mp4` (~160 MB) and `working/audio16k.wav` (~100 MB) exceed
GitHub's 100 MB per-file limit. They commit fine locally; if you push to GitHub, use
[Git LFS](https://git-lfs.com/) for these (or keep them local-only).

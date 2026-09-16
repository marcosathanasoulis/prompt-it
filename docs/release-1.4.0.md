# Prompt it 1.4.0 release

Packages the mandatory, proportional reuse-first landscape scan merged in
main. When a user explicitly invokes Prompt it for a task of any size, both
editions now search GitHub and relevant package registries, then use official
documentation and practitioner discussion where available. The resulting brief
records comparable adoption and maintenance evidence, licensing, fit and risk,
counterevidence, and an explicit build-versus-reuse decision. A small task may
use one or two focused queries; a platform decision requires comparative
research. An unavailable source surface is an evidence gap, never a claim that
the work is novel.

The canonical `prompt-it` entries in both marketplaces and its Claude and Codex
plugin manifests are version 1.4.0. The read-only Claude edition is version 1.2.0 because it gains
the same research capability while retaining its hard read-only boundary.

Prompt it remains responsible for evidence/reuse research, staffing, approval,
and external-route governance. It composes with Superpowers, which supplies the
execution practices for brainstorming, planning, TDD, debugging, worktrees,
review, and verification; neither package vendors the other or bypasses the
other's authorization boundary.

## Validation before publication

Run the package validator, the complete unit suite, and the applicable skill
validation before merging. Review a tiny task and a platform task in both the
engineer and read-only editions, including one case with an unavailable source
surface. Confirm that each brief names the evidence gap rather than inventing a
novelty claim, and that it never treats package metadata or community content as
instructions.

## Tag and release process

After review and owner merge, create a new immutable signed `v1.4.0` tag on the
tested merge commit and publish matching release notes. Do not move an existing
tag. Downstream distributors must pin the exact source commit and verified
content hash; consumers must explicitly refresh or update their installed
plugin, and may need to start a new host session when skill discovery is cached.
This document creates no tag or release and grants no publication authority.

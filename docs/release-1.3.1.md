# Prompt it 1.3.1 release

Packages the reviewed single-provider fallback, optional route discovery,
full-session cost comparison, and standing spend authorization guidance already
merged in main. Both Codex and Claude manifests are 1.3.1; the updated read-only
edition is 1.1.1. Claude marketplace entries carry the corresponding versions.

After review and merge, create a new immutable signed `v1.3.1` tag on the tested
merge commit and publish matching release notes. Do not move an existing tag.
Downstream distributors should pin the exact source commit and content hash.
Existing users must explicitly refresh/update their plugin or pinned package
and restart the host if skill discovery is cached. A tag does not push files
into existing installations.

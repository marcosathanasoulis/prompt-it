# Prompt it 1.5.0 release

Adds an optional compatibility contract for exporting an approved canonical
Prompt it execution brief into an existing GitHub Spec Kit or OpenSpec
workflow. The export is one-way and maps only facts, decisions, task nodes, and
acceptance evidence already present in the approved brief. Prompt it retains
authority over approval, staffing, coordinator identity, evidence provenance,
and execution.

Exports refuse material unresolved questions, preserve proportional behavior
for small tasks, and never install or initialize target tools, vendor their
templates, recreate their validators, or import derived changes into the
canonical brief. An upstream validator may run only when the exact invocation
is part of the approved export node and current runtime authority permits it.

OpenSpec `MODIFIED` guidance follows the upstream replacement model: the delta
contains the complete new requirement, every current scenario that survives
the change, and the approved additions or edits.

## Validation before publication

Run the package validator and complete unit suite, check every tracked version
site and the changelog, scan and export the component, and compare it with the
public repository. Evaluate the supplied export scenarios, including denied
validator authority, derived drift, a surviving OpenSpec scenario, and a tiny
task with no initialized target.

## Tag and release process

This source change does not publish, tag, or release anything. After review,
owner merge, and validation of the merge commit, publish the component first:

```sh
python3 scripts/publish_public_components.py publish \
  --component prompt-it \
  --dev-tools-sha <tested-dev-tools-merge-sha>
```

The publisher prints `published prompt-it 1.5.0 ... as <public_sha>`. In an
up-to-date clone of the public Prompt it repository, fetch `main`, sign the
immutable tag on that exact returned public commit, push the tag, and create the
release from the generated notes:

```sh
git fetch origin main
git -c gpg.format=ssh \
  -c user.signingkey=~/.ssh/google_compute_engine.pub \
  tag -s v1.5.0 <public_sha> -m "prompt-it 1.5.0"
git push origin v1.5.0
gh release create v1.5.0 --verify-tag \
  --notes-file release-notes-prompt-it-1.5.0.md
```

The dev-tools merge SHA is provenance supplied to `publish`; it is not the
commit to tag. Do not tag before publication, tag the dev-tools merge commit,
move an existing tag, or publish from this worktree.

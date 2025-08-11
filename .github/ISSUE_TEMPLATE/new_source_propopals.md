---
name: New source proposal
about: Propose adding a new meme source (API or scraping)
title: "[Source]: <site / subreddit / feed name>"
labels: enhancement
assignees: ""
---

## Summary
Short description of the source and why it’s valuable.

## Source details
- Primary URL(s):
- Content types: (images / GIFs)
- Access method: (public HTML / API)
- Authentication required?: (no / API key / OAuth)
- Rate limits / quotas:
- Licensing / Terms of Use:

## Sample items
Links to a few example posts/images.

## Parsing approach
How to fetch and parse (selectors/endpoints). Mention any libraries.

## Output path & naming
Proposed destination paths, e.g. `memes/<source>/{originals|picked}/...`

## Success criteria
- [ ] Can fetch at least one valid meme
- [ ] Title overlay renders correctly (image/GIF)
- [ ] Files saved to expected paths
- [ ] Document any new config/env vars

## Additional context
Anything else reviewers should know.
# Add a campus or course

The public source of truth is editable files under `content/`. Generated `web/catalog.json` is checked into source so a release runs immediately. Run `python3 scripts/build.py` after editing and `python3 scripts/build.py --check` before committing.

## Campus

Edit `content/campuses.json`: use a stable, unique lowercase ID, display name, context and suggested rhythm. These are planning contexts sharing the same library; they do not store people or restrict education by gender. Add or remove local contexts freely. A campus rhythm is a discussion template, not a timetable imposed on a community.

## Course and lesson

Edit `content/courses.json` to describe course ID/title, levels and available weeks. Add Markdown files under `content/lessons/` and entries in `content/lessons/index.json`. Each entry needs a stable ID, course ID, title, collection (`student` or `teacher`), week, language (`amdo` or `english`), levels, relative path and review status. For another language pack, extend the documented language choices and portal filters together.

Student and teacher guides should be separate files. Teacher files include answers and correction notes. Level tags describe the levels covered by a document, not a claim that the app generates differentiated content. The initial guides combine L1–L4; filtering by level selects relevant documents while retaining their full text.

Give each activity an objective, learner task, optional partner/teacher response, review criteria and printable or zero-tech alternative. Use plain Unicode text for Tibetan, specify dialect and distinguish transliteration from pronunciation. Cite any third-party material with its compatible redistribution permission. Do not invent a quotation or add a copyrighted translation without permission.

## School templates

Edit Markdown files under `content/school/` and their records in `content/school/index.json`. Templates should guide human planning without asserting a campus is operating or making decisions about people. Never include real learner information, credentials, internal project URLs or private service bindings.

## Review and build

Review identity, provenance, permissions, language, pedagogy, accessibility and answer separation before promoting a lesson beyond `draft`. State the scope of actual educator review. The build validates catalog structure and produces a deterministic local catalog; tests verify the server and distribution boundaries. Neither substitutes for qualified teaching review.

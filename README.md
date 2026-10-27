# School in a Box

**An open source, offline learning and teaching starter kit.** Download it, run it on a laptop or small computer, and adapt it for your school or community. No account, cloud service, AI provider, subscription, or Python package installation is required to use the local portal.

[Try the browser demo](https://pqexpert.io/school-in-a-box/) · [Download a release](https://github.com/pqexpert/school-in-a-box/releases/latest) · [Contribute a lesson or correction](CONTRIBUTING.md)

The first course is **Amdo Tibetan ↔ English**, adapted from the DABA learning-through-teaching project. It includes two weeks, eight teacher/student lesson files, four learning levels, and adaptable community, boys, girls, and monastic campus planning templates. Campus templates share the same learning resources and do not assign ability or subjects by gender.

**Status: v0.1 starter kit.** This is a working course library and school planning kit. It is not a complete accredited school, a validated Tibetan curriculum, a student information system, or an autonomous school operator. The broader 36-week course is a roadmap. Language material needs fluent educator review before classroom reliance.

## Start in three steps

1. [Download the latest release](https://github.com/pqexpert/school-in-a-box/releases/latest) and extract the ZIP, or clone this repository.
2. Install Python 3.11 or newer if needed. On Windows, `py` can replace `python3` below.
3. From the extracted project folder, run:

```sh
python3 server.py
```

Open **http://127.0.0.1:8080**. Stop with Ctrl+C. The portal works without internet once downloaded. For an occupied port, run `python3 server.py --port 8081` and open that port instead.

## What is in the box?

| Area | Available now |
| --- | --- |
| Learn | Week 1: Identity; Week 2: Hospitality; Amdo and English activities |
| Teach | Embedded answer guides, L1–L4 activities, peer teaching, print view |
| Campus | Editable local context, timetable, responsibilities and resource planning templates |
| Course | Published two-week scope, four-level progression, review checklist and 36-week roadmap |
| Personal practice | Browser-local notes, practice markers, JSON export and import |
| Access | Search, course/week/language/level filters, responsive reading layout |
| Distribution | Source code, editable Markdown content, static site export, offline release ZIP and SHA-256 checksum |

Choose a campus context, then Learn, Teach, or School. Campus selection provides planning context; it does not create campuses, enroll students, or enforce permissions. Teacher and student collections are navigation views of openly licensed material, including answer keys.

## Share and adapt

For a small trusted classroom LAN, follow [local deployment](docs/DEPLOYMENT.md). For a public static website, run `python3 scripts/build.py --output site` and host the resulting `site/` folder. No external requests are required by the portal. The built-in Python server is intended for local/trusted use; public internet serving should use a maintained static host or web server.

Edit [campus settings](content/campuses.json), [course settings](content/courses.json), and [lesson Markdown](content/lessons). Run `python3 scripts/build.py` after changes. See [the content guide](docs/CONTENT.md) and [school setup](content/school/start-here.md).

The content pack supports a secular community classroom and optional locally approved cultural study. This community project makes no claim of endorsement by Dzokden, a monastery, a government, an educational authority, or a Tibetan lineage.

## Privacy and limits

The portal has no accounts, server database, analytics, tracking, credentials, or outbound API calls. Notes stay in your browser profile; export them for backup and clear them on shared computers. Only record your own study reflections. This version has no student records, attendance, grades, safeguarding case management, health logging, payments, remote management, translation model, or automated decisions about people.

Teacher review, safeguarding, consent, accessibility, local requirements, and meaningful community leadership remain human responsibilities. No code provisions Wi-Fi, changes firewalls, or launches agents. Optional school plans are templates, not claims of campus operations.

## License and contribution

- Software and technical documentation: **[MIT](LICENSE)**.
- `content/` and generated educational text: **[CC BY 4.0](LICENSE-CONTENT.md)**. Credit “School in a Box contributors / DABA project,” link to this repository and license, and identify adaptations.
- Names identify project context; the licenses do not imply endorsement or license third-party trademarks.

See [provenance](docs/PROVENANCE.md), [contribution guidance](CONTRIBUTING.md), [community conduct](CODE_OF_CONDUCT.md), and [roadmap](docs/ROADMAP.md). Contributions of fluent Tibetan review, accessible lesson design, translations, tested offline deployments, and openly licensed course packs are welcome.

## Verify and package

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
python3 scripts/package.py --version v0.1.0
```

The release ZIP includes the full editable project and can be carried on USB. Build and test tools use only the Python standard library. A pinned GitHub Actions example is provided in `docs/ci.example.yml`; maintainers can install it under `.github/workflows/` when their credentials permit workflow publication. No automatic CI run is claimed by this release. A local verification result is not proof of field deployment or educator approval.

# How to deprecate, move or version a RAPP/1 repo

Every public RAPP repo of kody-w is a station of the RAPP/1 network. Its portfolio file, its badge, the subway map,
the [notices page](https://kody-w.github.io/rapp-hive-public/portfolio/NOTICES.html) and each crawl's pulse show its version, its channel and its lifecycle. This
page says how to change them, in plain words. A step marked **(owner)** only the owner can do: it needs the owner's
GitHub account or a signed save in the owner's RAPP Hive. Everything else follows from the next crawl.

## Deprecate a repo

1. **(owner)** Save a notice in the RAPP Hive by signed save: the file `shared/organism/notices/<repo>.md`, which
   the public copy serves as `notices/<repo>.md`. The package writes it and asks the Hive for its signed save (the
   same save a crawl uses):

   ```
   python -m rapp1_network notice <repo> --lifecycle deprecated --since 2026-10-01 --notice "Use rapp-example instead; this repo gets no new features."
   ```

   `--dry-run` prints the file and changes nothing, and `python -m rapp1_network notice check` checks every notice
   file in the Hive. By hand, the file is:

   ```
   ---
   repo: kody-w/<repo>
   lifecycle: deprecated
   since: 2026-10-01
   notice: "One line of plain text, 1 to 200 characters."
   ---

   Anything else you want to say, in markdown.
   ```

   The keys come in this order. The notice is one line of plain text in double quotes, without Liquid or kramdown
   markers (a brace followed by another brace, a percent sign or a colon). The folder holds notice files only. A
   notice file that breaks a rule stops the next cut with a message that names the file and the rule, and so does a
   notice for a repo that is not in the portfolio.
2. **(owner)** Say it in the repo's own README too, near the top. The README is the repo's front door and stays
   editable; its network header (the badge and "Start here") stays where it is.
3. The next crawl changes the rest: the badge reads **deprecated** first (then the version, when there is one); the
   repo's portfolio file leads with the notice; PORTFOLIO.md shows it first in the Status column; the subway map
   draws the station hollow; the notices page lists it; and the pulse records the lifecycle, its date and the
   notice, so the [timeline](https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html) lists the change.

To take a notice back: `python -m rapp1_network notice <repo> --clear` (a signed save that removes the file). The
next crawl shows the repo as active again.

## Move a repo

1. **(owner)** Make the successor a new repo with its own network header (its badge and "Start here"), so the crawl
   checks it as a station of its own.
2. **(owner)** Save a `superseded` notice for the old repo that names its successor:

   ```
   python -m rapp1_network notice <old repo> --lifecycle superseded --since 2026-10-01 --superseded-by <new repo> --notice "Moved to <new repo>."
   ```

   The successor is a repo of the portfolio (its name) or any `owner/repo`. While both are on the subway map, a
   dashed arrow runs from the old station to the new one.
3. A new repo and a notice are safer than a GitHub rename. A rename redirects the repo's page, its git URL and its
   raw file links for now, but never its GitHub Pages site, and a repo made later under the old name ends every
   redirect, so raw and Pages links that name the old repo can break. The old repo, left where it is, keeps every
   link working.
4. **(owner)** Archive the old repo on GitHub when you are ready. The crawl then shows it as **archived** (a dashed
   hollow station): an archived repo that was a station stays on the notice board instead of vanishing, and GitHub's
   archived wins over the notice, whose text stays.

A repo that leaves the family (deleted, made private or renamed away) keeps its portfolio file and its badge, which
turns grey and says `left`: it goes off the map and out of the totals, and the notices page lists it. A repo that
the private denylist holds back is removed instead: privacy wins.

## Version a repo

1. **(owner, or anyone who can push to the repo)** Give it a version: a root file named exactly `VERSION` whose first
   line is the version (for example `1.2.3`), or a GitHub release, whose tag is the version. When both exist, the
   VERSION file wins. A version is 1 to 40 letters, digits, dots, underscores, plus and minus signs, starting with a
   letter or a digit; anything else is not shown.
2. The next crawl records it: the badge adds it (`v1.2.3`; a tag such as `v1.0.0` stays as it is), and the repo's
   portfolio file, PORTFOLIO.md and the pulse show it.
3. The LTS pin comes from the estate's LTS pins (a file the crawl is given with `--lts-pins`); until the estate
   publishes them, from the known pins built into the package: rapp-1 at `591e014` (the canon pin every check runs
   at), rapp-installer at `brainstem-v0.6.9`, rapp-work at `29ead23` and rapp-map at `4c8ba6b`. A repo with an LTS
   pin is on the channel **rapp1-lts**; every other repo is on **newest**.
4. **(owner)** A later LTS is a new `release_scope` in the estate's LTS pins, never an edit of a published one: a
   published pin, like a published pulse, never changes.

## What only the owner can do

Save or clear a notice (a signed save in the RAPP Hive), archive or rename a repo on GitHub, and change the estate's
LTS pins. The crawl reads all of them and changes nothing by itself.

[Notices](https://kody-w.github.io/rapp-hive-public/portfolio/NOTICES.html) · [Portfolio](https://kody-w.github.io/rapp-hive-public/portfolio/PORTFOLIO.html) · [Subway map](https://kody-w.github.io/rapp-hive-public/portfolio/subway.html) ·
[Timeline](https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html)

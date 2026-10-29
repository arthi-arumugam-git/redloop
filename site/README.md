# RedLoop landing page (static)
To publish with GitHub Pages:
1. Pages only serves from `/` or `/docs`, so copy the page there: `mkdir -p docs && cp site/index.html docs/` and push. (The other option is a GitHub Actions Pages workflow that uploads `site/`.)
2. In the repo, go to Settings → Pages → Source and pick "Deploy from a branch", then branch `main`, folder `/docs`.
3. The site will be live at https://arthi-arumugam-git.github.io/redloop/
4. Once Gumroad is published, swap the "Buy the kit — link after publish" placeholder for the real link.

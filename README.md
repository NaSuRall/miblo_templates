# Miblo templates

Versioned template packs for Miblo CLI. Templates stay outside the CLI binary
and can be distributed as archives on GitHub Releases or another HTTPS server.

| Directory | Database | Pack version | CLI compatibility |
| --- | --- | --- | --- |
| `rust_template_v4/` | MySQL | 0.6.0 | 0.9+ |
| `rust_sqlite_template_v4/` | SQLite | 0.6.0 | 0.9+ |
| `rust_template_v3/` | MySQL | 0.5.0 | 0.8+ |
| `rust_sqlite_template_v3/` | SQLite | 0.5.0 | 0.8+ |
| `rust_template_v2/` | MySQL | 0.4.0 | 0.7+ |
| `rust_sqlite_template_v2/` | SQLite | 0.4.0 | 0.7+ |
| `rust_template_v1/` | MySQL | 0.3.0 | 0.5+ |
| `rust_sqlite_template_v1/` | SQLite | 0.3.0 | 0.5+ |

The current packs use format 3 and declare `relations`, `layered-resources`, `custom-routes` and `model-routes`.
Format 1 and 2 packs are kept unchanged for existing projects. They generate
Axum + SQLx CRUD APIs with automatic integer primary keys, optional/required
foreign keys, indexes and RESTRICT / CASCADE / SET NULL deletion rules.
The previous MySQL v0.1.0 and SQLite v0.2.0 release assets remain immutable;
projects pinned to them can still use CLI 0.5 and opt into the newer templates.
`rust_template/` is the legacy format, kept for reference.

## Use the published release

With Miblo CLI 0.9 installed, no local template checkout is needed:

```sh
miblo new my-api --database sqlite
# Or: miblo new my-api --database mysql
```

In the full-screen `miblo` interface, create an API and choose **GitHub Releases**.
The CLI downloads the matching archive from the
[v0.6.0 release](https://github.com/NaSuRall/miblo_templates/releases/tag/v0.6.0),
checks its SHA-256 sidecar and caches it. An existing `MIBLO_TEMPLATE_DIR` selects
a local pack in the direct CLI; unset it to use the default remote source.

For an existing API, press **u** in Miblo or run `miblo template update` in the
project. Only the pack used for **future** models and routes is updated (existing models keep their original pack for later edits): existing source,
custom error handlers and applied migrations are preserved. The registry must
remain compatible. Then add a new model and select **Ajouter une relation** in
the fields menu, or use `group_id:int:ref=Group` in CLI fields. The target model
must already exist; optional self references are also supported.

Press **d** to inspect the real database schema and **p** to compare it with the
declared models. Templates remain separate from the binary; CLI 0.9 is required
for the format-3 layout. Template releases do not publish the crate.

## Readable generated applications

Each model has a folder with six focused files:

- `mod.rs`: route definitions;
- `handlers.rs`: HTTP extraction and JSON/status responses;
- `model.rs`: stored fields and response serialization;
- `requests.rs`: named creation/update payloads, pagination, validation and tests;
- `service.rs`: business rules and calls to the repository;
- `repository.rs`: SQL queries, bindings, transactions and database errors.

Business code belongs in `service.rs`. Field additions do not rewrite handlers
or services; model, request and SQL updates use Miblo's existing merge protection.
The startup is split into `main.rs`, `config.rs`, `database.rs` and `lib.rs`.
All generated Rust is formatted before writing. The comments and practical README
are in French, with customization guidance, curl examples and migration commands.
The application runs independently with Cargo after generation.

The current packs keep format 3 and add the `model-routes` capability, which
requires CLI 0.9. Existing sources and released assets are unchanged. Miblo 0.9
can use all three formats, including both layouts in a single project after a template
update; it remembers the template for each model.

## Use locally

With both repositories next to one another:

```sh
cd ../Miblo
cargo run -- new demo-api --database mysql --template-dir ../miblo_templates/rust_template_v4
```

## Build a release archive

```sh
python3 scripts/package.py
# SQLite:
python3 scripts/package.py --source rust_sqlite_template_v4
```

The script produces deterministic files under `dist/v0.6.0/`:

- `rust-axum-mysql.tar.gz`;
- `rust-axum-mysql.tar.gz.sha256`.

With the SQLite source, it produces `dist/v0.6.0/rust-axum-sqlite.tar.gz`
and `rust-axum-sqlite.tar.gz.sha256` instead.

The archive contains `manifest.json` and the `.hbs` files directly at its root,
without a repository-name wrapper directory. No scripts run during template
loading. Project files include a Cargo.lock so the tested dependency resolution
is preserved in newly generated APIs.

For each new version, test the exact archive, commit its template sources and
packaging script, then attach both files to the corresponding `v<VERSION>`
release of `NaSuRall/miblo_templates`. Tag that exact source commit. The packaging
script does not publish anything. Never replace the contents of a published version: update
`manifest.json`, test the pack, and release a new version instead.

For a custom HTTP server, keep this layout:

```text
v0.6.0/
  rust-axum-mysql.tar.gz
  rust-axum-mysql.tar.gz.sha256
```

Use `--template-base-url https://your-server.example/templates` in Miblo.
For a local download test, serve `dist/` on loopback and use its HTTP URL.

## Pack contract

The manifest contains `schema_version`, `id`, `version` and `features`.
Format 2 adds `project/config.rs.hbs`, `project/database.rs.hbs` and the three
resource templates `requests.rs.hbs`, `service.rs.hbs`, `repository.rs.hbs`. Miblo validates the
pack and requires the exact file names listed in its `src/templates.rs`.

- `project/`: one-time application scaffold and dependency lockfile;
- `resource/`: files created for each new resource and its migration;
- `registry.rs.hbs`: managed resource registration.

Keep application decisions out of the template language where possible. The
CLI supplies validated resource names, SQL types, Rust types, collection paths
and field constraints. The `relations` context supplies validated foreign-key
fields, target tables, delete actions and deterministic index names. Templates cannot run shell commands during generation.

When changing dependencies, regenerate and review `project/Cargo.lock.hbs`
from a generated project; replace only that project's package name with the
`{{project_name}}` placeholder. Preserve its package version `0.1.0`.

## Verify the actual output

From the CLI repository, run:

```sh
cargo build --locked
python3 scripts/smoke_mysql.py \
  --miblo target/debug/miblo \
  --templates ../miblo_templates/rust_template_v4
```

The script uses an isolated temporary MySQL instance, tests real HTTP CRUD,
nullable PATCH, private response fields, validation and addition of resources
after custom edits and formatting. It needs installed `mysql` and `mysqld`.

After publishing, replace `--templates ../miblo_templates/rust_template_v3` with
`--remote` to test the default public download with an initially empty cache,
then resource addition offline from that cache and the same MySQL CRUD checks.

SQLite can be checked without a database server using the CLI repository's
`scripts/smoke_sqlite.py --miblo target/debug/miblo --templates
../miblo_templates/rust_sqlite_template_v3 --target-dir target/sqlite-smoke`.
Replace `--templates ...` with `--remote` after publication. The test checks
automatic setup, tables, CRUD, concurrent updates and persistence across restarts.

Legacy sample connection values have been replaced with placeholders. If real
credentials from the old files were used elsewhere, replace them there too;
editing the current sample does not remove values from Git history.

### Routes personnalisées (format 3)

Les packs `rust_template_v3` et `rust_sqlite_template_v3` ajoutent la fonctionnalité
`custom-routes` pour Miblo 0.8.0. Le dossier `route/` fournit le registre, les erreurs
et quatre fichiers par route : module, handler HTTP, paramètres et service métier.
Le service répond 501 jusqu’à son implémentation. Aucun changement SQL n’est généré.
Les dossiers v1 (0.3.0) et v2 (0.4.0) restent inchangés pour les projets épinglés.

### Routes CRUD liées aux modèles (0.6.0, format 3)

Les nouveaux dossiers `rust_template_v4` et `rust_sqlite_template_v4` déclarent
la fonctionnalité `model-routes`. Ils conservent le format d’archive 3.
Miblo 0.9 permet de choisir un modèle et une action CRUD, avec méthode HTTP et
contrat JSON déduits. La route génère un module et un alias vers le handler du
modèle : ses validations et ses requêtes SQL sont ainsi réutilisées, y compris
pour les anciens modèles. Aucun code du modèle, aucune migration n’est réécrit.

Les routes à logique personnalisée conservent leurs quatre fichiers et leur
réponse initiale 501. Les packs 0.5.0 publiés restent inchangés.

```sh
python3 scripts/package.py --source rust_template_v4
python3 scripts/package.py --source rust_sqlite_template_v4
```

Les archives et leurs sommes SHA-256 se trouvent dans `dist/v0.6.0/`.

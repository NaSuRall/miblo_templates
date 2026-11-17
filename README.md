# Miblo templates

Versioned template packs for Miblo CLI. Templates stay outside the CLI binary
and can be distributed as archives on GitHub Releases or another HTTPS server.

`rust_template_v1/` contains format 1, stack `rust-axum-mysql`, version `0.1.0`.
It targets Miblo CLI 0.2 and creates an Axum + SQLx + MySQL CRUD API without
authentication. `rust_template/` is the legacy format and is kept for reference;
its old configuration is not compatible with the new CLI.

## Use the published release

With Miblo CLI 0.2 installed, no local template checkout is needed:

```sh
miblo new my-api
```

In the full-screen `miblo` interface, create an API and choose **GitHub Releases**.
The CLI downloads the [v0.1.0 release](https://github.com/NaSuRall/miblo_templates/releases/tag/v0.1.0),
checks the archive against its SHA-256 sidecar, and caches it for subsequent use.
An existing `MIBLO_TEMPLATE_DIR` environment variable selects a local pack in the
direct CLI; unset it to use the default remote source.

Template releases and the CLI crate are published separately. This release
provides the pack for the 0.2 CLI; it does not publish a new crate to crates.io.

## Use locally

With both repositories next to one another:

```sh
cd ../Miblo
cargo run -- new demo-api --template-dir ../miblo_templates/rust_template_v1
```

## Build a release archive

```sh
python3 scripts/package.py
```

The script produces deterministic files under `dist/v0.1.0/`:

- `rust-axum-mysql.tar.gz`;
- `rust-axum-mysql.tar.gz.sha256`.

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
v0.1.0/
  rust-axum-mysql.tar.gz
  rust-axum-mysql.tar.gz.sha256
```

Use `--template-base-url https://your-server.example/templates` in Miblo.
For a local download test, serve `dist/` on loopback and use its HTTP URL.

## Pack contract

The manifest contains `schema_version`, `id` and `version`. Miblo validates the
pack and requires the exact file names listed in its `src/templates.rs`.

- `project/`: one-time application scaffold and dependency lockfile;
- `resource/`: files created for each new resource and its migration;
- `registry.rs.hbs`: managed resource registration.

Keep application decisions out of the template language where possible. The
CLI supplies validated resource names, SQL types, Rust types, collection paths
and field constraints. Templates cannot run shell commands during generation.

When changing dependencies, regenerate and review `project/Cargo.lock.hbs`
from a generated project; replace only that project's package name with the
`{{project_name}}` placeholder. Preserve its package version `0.1.0`.

## Verify the actual output

From the CLI repository, run:

```sh
cargo build --locked
python3 scripts/smoke_mysql.py \
  --miblo target/debug/miblo \
  --templates ../miblo_templates/rust_template_v1
```

The script uses an isolated temporary MySQL instance, tests real HTTP CRUD,
nullable PATCH, private response fields, validation and addition of resources
after custom edits and formatting. It needs installed `mysql` and `mysqld`.

After publishing, replace `--templates ../miblo_templates/rust_template_v1` with
`--remote` to test the default public download with an initially empty cache,
then resource addition offline from that cache and the same MySQL CRUD checks.

Legacy sample connection values have been replaced with placeholders. If real
credentials from the old files were used elsewhere, replace them there too;
editing the current sample does not remove values from Git history.

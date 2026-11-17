#!/usr/bin/env python3
"""Build a deterministic release archive and its SHA-256 sidecar. Does not publish."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1] / 'rust_template_v1')
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'dist')
args = parser.parse_args()
manifest = json.loads((args.source / 'manifest.json').read_text())
assert manifest['schema_version'] == 1 and manifest['id'] == 'rust-axum-mysql'
version = manifest['version']
assert version and all(c.isascii() and (c.isalnum() or c in '.-_') for c in version)
output = args.output / ('v' + version)
output.mkdir(parents=True, exist_ok=True)
archive = output / 'rust-axum-mysql.tar.gz'
files = sorted([args.source / 'manifest.json', *args.source.rglob('*.hbs')])
buffer = io.BytesIO()
with gzip.GzipFile(fileobj=buffer, mode='wb', mtime=0, filename='') as gz:
    with tarfile.open(fileobj=gz, mode='w', format=tarfile.USTAR_FORMAT) as tar:
        for path in files:
            assert path.is_file() and not path.is_symlink()
            data = path.read_bytes()
            info = tarfile.TarInfo(path.relative_to(args.source).as_posix())
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
data = buffer.getvalue()
archive.write_bytes(data)
checksum = hashlib.sha256(data).hexdigest()
archive.with_suffix(archive.suffix + '.sha256').write_text(f'{checksum}  {archive.name}\n')
print(archive)
print(f'SHA-256: {checksum}')

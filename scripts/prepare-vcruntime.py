"""Extract AMD64 VC runtime DLLs from Microsoft's signed Burn installer."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

DLLS = (
    'concrt140.dll', 'msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll',
    'msvcp140_atomic_wait.dll', 'msvcp140_codecvt_ids.dll', 'vcamp140.dll',
    'vccorlib140.dll', 'vcomp140.dll', 'vcruntime140.dll',
    'vcruntime140_1.dll', 'vcruntime140_threads.dll',
)


def is_amd64(path):
    with path.open('rb') as f:
        dos = f.read(64)
        if len(dos) != 64 or dos[:2] != b'MZ':
            return False
        f.seek(struct.unpack_from('<I', dos, 0x3C)[0])
        return f.read(6) == b'PE\0\0\x64\x86'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--installer', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    destination = root / 'app/Madeira/x86_64-vcruntime'
    installer = args.installer or root / 'toolchains/downloads/vc_redist.x64.exe'
    if not installer.is_file():
        installer.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['curl', '-fL', 'https://aka.ms/vc14/vc_redist.x64.exe', '-o', str(installer)], check=True)
    data = installer.read_bytes()
    sevenzip = shutil.which('7zz') or shutil.which('7z')
    expand = shutil.which('expand.exe') if not sevenzip else None
    if not sevenzip and not expand:
        raise SystemExit('7-Zip is required to extract Microsoft cabinet payloads')

    with tempfile.TemporaryDirectory(prefix='madeira-vcruntime-') as temp:
        scratch = Path(temp)
        queue = deque()
        offset = 0
        while (offset := data.find(b'MSCF', offset)) >= 0:
            if offset + 36 <= len(data):
                size = struct.unpack_from('<I', data, offset + 8)[0]
                folders, files = struct.unpack_from('<HH', data, offset + 26)
                if data[offset + 24:offset + 26] == b'\x03\x01' and 36 < size <= len(data) - offset and folders and files:
                    cab = scratch / f'embedded-{offset}.cab'
                    cab.write_bytes(data[offset:offset + size])
                    queue.append(cab)
            offset += 4
        if not queue:
            raise SystemExit('No valid embedded cabinets found in the Microsoft installer')

        visited = set()
        extracted = []
        while queue:
            cab = queue.popleft()
            digest = hashlib.sha256(cab.read_bytes()).digest()
            if digest in visited:
                continue
            visited.add(digest)
            out = scratch / f'extracted-{len(visited)}'
            out.mkdir()
            command = ([sevenzip, 'x', '-y', str(cab), '-o' + str(out)] if sevenzip
                       else [expand, '-F:*', str(cab), str(out)])
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.returncode:
                raise SystemExit(result.stdout.decode(errors='replace'))
            for entry in out.rglob('*'):
                if not entry.is_file():
                    continue
                extracted.append(entry)
                with entry.open('rb') as f:
                    if f.read(4) == b'MSCF':
                        queue.append(entry)

        verified = {}
        for dll in DLLS:
            # ARM64X payloads can advertise an AMD64 PE header too. Prefer
            # Microsoft's explicitly labelled AMD64 file over other payloads.
            candidates = [p for p in extracted if p.name.lower() == dll + '_amd64']
            if not candidates:
                candidates = [p for p in extracted if p.name.lower() == dll]
            candidates = [p for p in candidates if is_amd64(p)]
            if not candidates:
                raise SystemExit(f'Missing AMD64 runtime: {dll}')
            digests = {hashlib.sha256(p.read_bytes()).hexdigest() for p in candidates}
            if len(digests) != 1:
                raise SystemExit(f'Ambiguous AMD64 runtime: {dll}')
            verified[dll] = (candidates[0], digests.pop())
        destination.mkdir(parents=True, exist_ok=True)
        for dll, (source, _) in verified.items():
            shutil.copyfile(source, destination / dll)
        print(json.dumps({'cabinets_extracted': len(visited), 'architecture': 'AMD64',
                          'dll_sha256': {name: digest for name, (_, digest) in verified.items()}}, indent=2))


if __name__ == '__main__':
    main()

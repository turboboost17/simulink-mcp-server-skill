# Release Process

Use this process for public releases and internal registry promotion.

## Pre-Release Checklist

1. Update the version in `pyproject.toml`.
2. Update [CHANGELOG.md](../CHANGELOG.md).
3. Run unit tests that do not require MATLAB.
4. Run integration tests on a MATLAB workstation when available.
5. Generate or refresh the release lock file and SBOM.
6. Confirm no private paths, hostnames, IP addresses, license servers, or saved
   MathWorks documentation assets are tracked.

## Local Build

```powershell
py -3.12 -m venv .build-venv
.\.build-venv\Scripts\python.exe -m pip install --upgrade pip build
.\.build-venv\Scripts\python.exe -m build
Get-FileHash dist\* -Algorithm SHA256 | Format-Table
```

## Tagging

Use annotated version tags:

```powershell
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

The release workflow builds wheels and source distributions, creates SHA256
checksums, generates an SBOM, and uploads the files to the GitHub release.

## Release Artifacts

Each release should include:

- Wheel (`.whl`)
- Source distribution (`.tar.gz`)
- SHA256 checksum file
- CycloneDX SBOM
- Release notes summarizing tool changes, security controls, and upgrade notes

## Registry Promotion

For internal MCP registries, promote a specific tagged release rather than a
floating branch. Prefer separate registry profiles for `readonly`, `open`, and
`full` mode.
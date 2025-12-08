# CI/CD Integration

PyLynk automatically detects and captures CI/CD environment information when running in supported CI platforms. This metadata is sent with API requests during **upload operations only** to provide context about the build and deployment pipeline.

## Supported CI Platforms

- GitHub Actions
- Bitbucket Pipelines
- Azure DevOps
- Generic CI (any platform with `CI=true`)

## Automatic Metadata Extraction

When running in a CI environment during SBOM uploads, PyLynk automatically extracts:

| Category | Information |
|----------|-------------|
| Event | Event type (pull_request, push, release), release tag |
| Pull Request | PR number, URL, source/target branches, author |
| Build | Build ID, number, URL, commit SHA |
| Repository | Repository name, owner, URL |

## GitHub Actions

```yaml
name: Upload SBOM
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  upload-sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate SBOM
        run: |
          # Your SBOM generation command here

      - name: Upload SBOM to Interlynk
        env:
          INTERLYNK_SECURITY_TOKEN: ${{ secrets.INTERLYNK_TOKEN }}
        run: |
          python3 pylynk.py upload --prod 'my-product' --sbom sbom.json
```

## Bitbucket Pipelines

```yaml
pipelines:
  pull-requests:
    '**':
      - step:
          name: Upload SBOM
          script:
            - pip install -r requirements.txt
            - python3 pylynk.py upload --prod 'my-product' --sbom sbom.json
  tags:
    'v*':
      - step:
          name: Upload SBOM for Release
          script:
            - pip install -r requirements.txt
            - python3 pylynk.py upload --prod 'my-product' --sbom sbom.json
```

## Azure DevOps

```yaml
trigger:
  branches:
    include:
      - main
  tags:
    include:
      - v*

pr:
  branches:
    include:
      - main

steps:
  - script: pip install -r requirements.txt
    displayName: 'Install dependencies'

  - script: python3 pylynk.py upload --prod 'my-product' --sbom sbom.json
    displayName: 'Upload SBOM to Interlynk'
    env:
      INTERLYNK_SECURITY_TOKEN: $(INTERLYNK_TOKEN)
```

## Generic CI Support

For CI platforms not explicitly supported, PyLynk checks common environment variables when `CI=true`:

### Environment Variables

#### Event Type
| Variable | Description |
|----------|-------------|
| `EVENT_TYPE` | Event type (pull_request, push, release) |

#### Release
| Variable | Description |
|----------|-------------|
| `GIT_TAG`, `REPO_TAG`, `CI_COMMIT_TAG`, `TAG_NAME` | Git tag for release builds |

#### Pull Request
| Variable | Description |
|----------|-------------|
| `PULL_REQUEST_NUMBER`, `PR_NUMBER`, `CHANGE_ID` | PR number |
| `PR_URL` | Full URL to the pull request |
| `PR_AUTHOR`, `PULL_REQUEST_AUTHOR`, `PR_USER`, `CHANGE_AUTHOR`, `CI_COMMIT_AUTHOR` | PR author username |

#### Branches
| Variable | Description |
|----------|-------------|
| `BRANCH_NAME`, `REPO_BRANCH`, `GIT_BRANCH`, `PR_SOURCE_BRANCH` | Source branch |
| `PR_TARGET_BRANCH`, `BASE_BRANCH`, `TARGET_BRANCH` | Target branch |

#### Build
| Variable | Description |
|----------|-------------|
| `BUILD_ID`, `CI_BUILD_ID` | Build identifier |
| `BUILD_NUMBER` | Build number |
| `BUILD_URL` | Full URL to the build/pipeline |

#### Commit
| Variable | Description |
|----------|-------------|
| `GIT_COMMIT`, `REPO_COMMIT`, `COMMIT_SHA`, `SHA` | Git commit SHA |

#### Repository
| Variable | Description |
|----------|-------------|
| `REPO_URL`, `REPOSITORY_URL` | Repository URL |
| `REPO_NAME`, `REPOSITORY_NAME` | Repository name |

### Example Generic CI Setup

```bash
export CI=true
export EVENT_TYPE=pull_request
export PULL_REQUEST_NUMBER=123
export BRANCH_NAME=feature/new-feature
export PR_TARGET_BRANCH=main
export PR_URL=https://github.com/myorg/myrepo/pull/123
export PR_AUTHOR=john-doe
export BUILD_URL=https://ci.example.com/job/myproject/123/
export GIT_COMMIT=abc123def456789
export REPO_URL=https://github.com/myorg/myrepo

python3 pylynk.py upload --prod 'my-product' --sbom sbom.json
```

## Controlling Metadata Collection

Control CI metadata with the `PYLYNK_INCLUDE_CI_METADATA` environment variable:

```bash
# Disable CI metadata collection
export PYLYNK_INCLUDE_CI_METADATA=false

# Force enable (even outside CI)
export PYLYNK_INCLUDE_CI_METADATA=true

# Auto-detect (default)
export PYLYNK_INCLUDE_CI_METADATA=auto
```

**Behavior:**
- `auto` (default): Enabled when in CI environment AND running `upload` command
- `true`: Always enabled for upload operations
- `false`: Never included

## Viewing Extracted Information

Use `--verbose` to see what CI/CD information was extracted:

```bash
python3 pylynk.py upload --prod 'my-product' --sbom sbom.json --verbose
```

Output includes:
```
DEBUG - CI/CD Environment Information Extraction
DEBUG - CI Provider: github_actions
DEBUG - PR Information:
DEBUG -   number: 123
DEBUG -   url: https://github.com/org/repo/pull/123
DEBUG -   source_branch: feature/new-feature
DEBUG -   target_branch: main
DEBUG -   author: john-doe
DEBUG - Build Information:
DEBUG -   build_id: 456789
DEBUG -   build_url: https://github.com/org/repo/actions/runs/456789
DEBUG -   commit_sha: abc123def456
```

## HTTP Headers Sent

The extracted CI information is sent as HTTP headers with upload API requests:

| Header | Description | Example |
|--------|-------------|---------|
| `X-CI-Provider` | CI platform name | `github_actions`, `bitbucket_pipelines`, `azure_devops`, `generic_ci` |
| `X-Event-Type` | CI event type | `pull_request`, `push`, `release` |
| `X-Release-Tag` | Release tag name | `v1.2.3` |
| `X-PR-Number` | Pull request number | `123` |
| `X-PR-URL` | Pull request URL | `https://github.com/org/repo/pull/123` |
| `X-PR-Source-Branch` | PR source branch | `feature/new-feature` |
| `X-PR-Target-Branch` | PR target branch | `main` |
| `X-PR-Author` | PR author username | `john-doe` |
| `X-Build-URL` | Build URL | `https://github.com/org/repo/actions/runs/456789` |
| `X-Commit-SHA` | Git commit SHA | `abc123def456` |
| `X-Repository-URL` | Repository URL | `https://github.com/org/repo` |

**Note:** These headers are only sent during `upload` operations when CI metadata collection is enabled.

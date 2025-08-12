"""CI/CD environment information extraction module."""

import os
import json
import logging

logger = logging.getLogger(__name__)

class CIInfo:
    """Extract CI/CD environment information for GitHub Actions and Bitbucket Pipelines."""

    def __init__(self):
        self.ci_provider = self._detect_ci_provider()
        self.event_info = self._extract_event_info()
        self.build_info = self._extract_build_info()
        self.repository_info = self._extract_repository_info()

        if logger.isEnabledFor(logging.DEBUG):
            self._log_extracted_info()

    def _detect_ci_provider(self):
        if os.getenv('GITHUB_ACTIONS') == 'true':
            return 'github_actions'
        if os.getenv('BITBUCKET_BUILD_NUMBER'):
            return 'bitbucket_pipelines'
        if os.getenv('CI'):
            return 'generic_ci'
        return None

    def _extract_event_info(self):
        """Detect event type and collect context (PR, push, release/tag)."""
        event_info = {}

        if self.ci_provider == 'github_actions':
            event_name = os.getenv('GITHUB_EVENT_NAME', '')
            event_info['event_type'] = event_name

            event_path = os.getenv('GITHUB_EVENT_PATH')
            if event_name.startswith('pull_request') and event_path and os.path.exists(event_path):
                with open(event_path, 'r') as f:
                    event_data = json.load(f)
                pr = event_data['pull_request']
                event_info.update({
                    'number': pr['number'],
                    'url': pr['html_url'],
                    'source_branch': pr['head']['ref'],
                    'target_branch': pr['base']['ref'],
                    'author': pr['user']['login']
                })
            elif event_name == 'push':
                ref = os.getenv('GITHUB_REF', '')
                if ref.startswith('refs/heads/'):
                    event_info['source_branch'] = ref.split('/', 2)[-1]
                event_info['author'] = os.getenv('GITHUB_ACTOR')
            elif event_name == 'release' and event_path and os.path.exists(event_path):
                with open(event_path, 'r') as f:
                    event_data = json.load(f)
                release_data = event_data.get('release', {})
                event_info.update({
                    'release_tag': release_data.get('tag_name'),
                    'release_name': release_data.get('name'),
                    'author': release_data.get('author', {}).get('login')
                })

        elif self.ci_provider == 'bitbucket_pipelines':
            # Event type detection
            if os.getenv("BITBUCKET_PR_ID"):
                event_info['event_type'] = "pull_request"
                event_info.update({
                    'number': os.getenv('BITBUCKET_PR_ID'),
                    'url': f"https://bitbucket.org/{os.getenv('BITBUCKET_WORKSPACE')}/{os.getenv('BITBUCKET_REPO_SLUG')}/pull-requests/{os.getenv('BITBUCKET_PR_ID')}",
                    'source_branch': os.getenv('BITBUCKET_BRANCH'),
                    'target_branch': os.getenv('BITBUCKET_PR_DESTINATION_BRANCH'),
                    'author': os.getenv('BITBUCKET_STEP_TRIGGERER_UUID')
                })
                # Optional: API fetch for richer PR details could go here
            elif os.getenv("BITBUCKET_TAG"):
                event_info['event_type'] = "release"
                event_info.update({
                    'release_tag': os.getenv('BITBUCKET_TAG'),
                    'author': os.getenv('BITBUCKET_STEP_TRIGGERER_UUID')
                })
            elif os.getenv("BITBUCKET_BRANCH"):
                event_info['event_type'] = "push"
                event_info.update({
                    'source_branch': os.getenv('BITBUCKET_BRANCH'),
                    'author': os.getenv('BITBUCKET_STEP_TRIGGERER_UUID')
                })
            else:
                event_info['event_type'] = "unknown"

        else:
            # Generic CI fallback
            if os.getenv('PULL_REQUEST_NUMBER') or os.getenv('PR_NUMBER'):
                event_info['event_type'] = "pull_request"
                event_info['number'] = os.getenv('PULL_REQUEST_NUMBER') or os.getenv('PR_NUMBER')
            elif os.getenv('GIT_TAG'):
                event_info['event_type'] = "release"
                event_info['release_tag'] = os.getenv('GIT_TAG')
            else:
                event_info['event_type'] = "push"

        return {k: v for k, v in event_info.items() if v}

    def _extract_build_info(self):
        build_info = {}
        if self.ci_provider == 'github_actions':
            build_info.update({
                'build_id': os.getenv('GITHUB_RUN_ID'),
                'build_number': os.getenv('GITHUB_RUN_NUMBER'),
                'commit_sha': os.getenv('GITHUB_SHA'),
                'build_url': f"{os.getenv('GITHUB_SERVER_URL', 'https://github.com')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
            })
        elif self.ci_provider == 'bitbucket_pipelines':
            build_info.update({
                'build_number': os.getenv('BITBUCKET_BUILD_NUMBER'),
                'commit_sha': os.getenv('BITBUCKET_COMMIT'),
                'build_url': f"https://bitbucket.org/{os.getenv('BITBUCKET_WORKSPACE')}/{os.getenv('BITBUCKET_REPO_SLUG')}/pipelines/results/{os.getenv('BITBUCKET_BUILD_NUMBER')}"
            })
        # Fallbacks
        build_info.setdefault('commit_sha', os.getenv('GIT_COMMIT') or os.getenv('COMMIT_SHA') or os.getenv('SHA'))
        build_info.setdefault('build_id', os.getenv('BUILD_ID') or os.getenv('CI_BUILD_ID'))
        build_info.setdefault('build_url', os.getenv('BUILD_URL'))
        return {k: v for k, v in build_info.items() if v}

    def _extract_repository_info(self):
        repo_info = {}
        if self.ci_provider == 'github_actions':
            repository = os.getenv('GITHUB_REPOSITORY', '')
            if '/' in repository:
                repo_info['owner'], repo_info['name'] = repository.split('/', 1)
            repo_info['url'] = f"{os.getenv('GITHUB_SERVER_URL', 'https://github.com')}/{repository}" if repository else None
        elif self.ci_provider == 'bitbucket_pipelines':
            repo_info.update({
                'name': os.getenv('BITBUCKET_REPO_SLUG'),
                'owner': os.getenv('BITBUCKET_WORKSPACE'),
                'url': f"https://bitbucket.org/{os.getenv('BITBUCKET_WORKSPACE')}/{os.getenv('BITBUCKET_REPO_SLUG')}"
            })
        repo_info.setdefault('url', os.getenv('REPO_URL'))
        return {k: v for k, v in repo_info.items() if v}

    def _log_extracted_info(self):
        logger.debug("=" * 60)
        logger.debug(f"CI Provider: {self.ci_provider or 'Not detected'}")
        logger.debug(f"Event Info: {self.event_info or 'None'}")
        logger.debug(f"Build Info: {self.build_info or 'None'}")
        logger.debug(f"Repository Info: {self.repository_info or 'None'}")
        logger.debug("=" * 60)

    def get_metadata(self):
        return {
            k: v for k, v in {
                'ci_provider': self.ci_provider,
                'event': self.event_info,
                'build': self.build_info,
                'repository': self.repository_info
            }.items() if v
        }

    def get_event_context_string(self):
        """Human-readable event summary."""
        if not self.event_info:
            return None
        etype = self.event_info.get('event_type', 'unknown')
        parts = [etype]
        if etype == "pull_request" and self.event_info.get('number'):
            parts.append(f"PR #{self.event_info['number']}")
        if self.event_info.get('source_branch') and self.event_info.get('target_branch'):
            parts.append(f"{self.event_info['source_branch']} → {self.event_info['target_branch']}")
        elif self.event_info.get('source_branch'):
            parts.append(f"branch: {self.event_info['source_branch']}")
        if self.event_info.get('release_tag'):
            parts.append(f"tag: {self.event_info['release_tag']}")
        if self.event_info.get('author'):
            parts.append(f"by {self.event_info['author']}")
        return " ".join(parts)

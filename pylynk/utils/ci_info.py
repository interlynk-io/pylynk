"""CI/CD environment information extraction module."""

import os
import logging

logger = logging.getLogger(__name__)


class CIInfo:
    """Extract CI/CD environment information from GitHub Actions and Bitbucket Pipelines."""
    
    def __init__(self):
        """Initialize CI info extraction."""
        self.ci_provider = self._detect_ci_provider()
        self.pr_info = self._extract_pr_info()
        self.build_info = self._extract_build_info()
        self.repository_info = self._extract_repository_info()
        
        if logger.isEnabledFor(logging.DEBUG):
            self._log_extracted_info()
    
    def _detect_ci_provider(self):
        """Detect which CI provider is being used."""
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            return 'github_actions'
        elif os.environ.get('BITBUCKET_BUILD_NUMBER'):
            return 'bitbucket_pipelines'
        elif os.environ.get('CI'):
            return 'generic_ci'
        return None
    
    def _extract_pr_info(self):
        """Extract PR information based on CI provider."""
        pr_info = {
            'number': None,
            'url': None,
            'title': None,
            'author': None,
            'source_branch': None,
            'target_branch': None,
            'event_name': None
        }
        
        if self.ci_provider == 'github_actions':
            # GitHub Actions environment variables
            event_name = os.environ.get('GITHUB_EVENT_NAME', '')
            
            if event_name == 'pull_request':
                # PR number is available in the ref
                ref = os.environ.get('GITHUB_REF', '')
                if '/pull/' in ref:
                    try:
                        pr_number = ref.split('/pull/')[1].split('/')[0]
                        pr_info['number'] = pr_number
                        
                        # Construct PR URL
                        repo = os.environ.get('GITHUB_REPOSITORY', '')
                        server_url = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
                        if repo and pr_number:
                            pr_info['url'] = f"{server_url}/{repo}/pull/{pr_number}"
                    except (IndexError, ValueError):
                        logger.debug("Failed to parse PR number from GITHUB_REF")
                
                # Branch information
                pr_info['source_branch'] = os.environ.get('GITHUB_HEAD_REF')
                pr_info['target_branch'] = os.environ.get('GITHUB_BASE_REF')
                pr_info['author'] = os.environ.get('GITHUB_ACTOR')
                pr_info['event_name'] = event_name
        elif self.ci_provider == 'bitbucket_pipelines':
            # Bitbucket Pipelines environment variables
            pr_id = os.environ.get('BITBUCKET_PR_ID')
            if pr_id:
                pr_info['number'] = pr_id
                
                # Construct PR URL
                workspace = os.environ.get('BITBUCKET_WORKSPACE')
                repo_slug = os.environ.get('BITBUCKET_REPO_SLUG')
                if workspace and repo_slug:
                    pr_info['url'] = f"https://bitbucket.org/{workspace}/{repo_slug}/pull-requests/{pr_id}"
                
                # Branch information
                pr_info['source_branch'] = os.environ.get('BITBUCKET_BRANCH')
                pr_info['target_branch'] = os.environ.get('BITBUCKET_PR_DESTINATION_BRANCH')
                pr_info['author'] = os.environ.get('BITBUCKET_STEP_TRIGGERER_UUID')
        
        # Generic CI fallback - check common environment variables
        if not pr_info.get('number'):
            pr_info['number'] = (
                os.environ.get('PULL_REQUEST_NUMBER') or
                os.environ.get('PR_NUMBER') or
                os.environ.get('CHANGE_ID')
            )
        
        if not pr_info.get('source_branch'):
            pr_info['source_branch'] = (
                os.environ.get('BRANCH_NAME') or
                os.environ.get('GIT_BRANCH') or
                os.environ.get('PR_SOURCE_BRANCH')
            )
        
        if not pr_info['target_branch']:
            pr_info['target_branch'] = (
                os.environ.get('PR_TARGET_BRANCH') or
                os.environ.get('BASE_BRANCH') or
                os.environ.get('TARGET_BRANCH')
            )
        
        if not pr_info['url']:
            pr_info['url'] = os.environ.get('PR_URL')
        
        if not pr_info['author']:
            pr_info['author'] = (
                os.environ.get('PR_AUTHOR') or
                os.environ.get('PULL_REQUEST_AUTHOR') or
                os.environ.get('PR_USER') or
                os.environ.get('CHANGE_AUTHOR') or
                os.environ.get('CI_COMMIT_AUTHOR')  # GitLab CI
            )
        
        # Clean up None values
        return {k: v for k, v in pr_info.items() if v is not None}
    
    def _extract_build_info(self):
        """Extract build information."""
        build_info = {
            'build_id': None,
            'build_number': None,
            'build_url': None,
            'commit_sha': None,
            'commit_message': None
        }
        
        if self.ci_provider == 'github_actions':
            build_info['build_id'] = os.environ.get('GITHUB_RUN_ID')
            build_info['build_number'] = os.environ.get('GITHUB_RUN_NUMBER')
            build_info['commit_sha'] = os.environ.get('GITHUB_SHA')
            
            # Construct build URL
            repo = os.environ.get('GITHUB_REPOSITORY')
            run_id = build_info['build_id']
            server_url = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
            if repo and run_id:
                build_info['build_url'] = f"{server_url}/{repo}/actions/runs/{run_id}"
            
        elif self.ci_provider == 'bitbucket_pipelines':
            build_info['build_number'] = os.environ.get('BITBUCKET_BUILD_NUMBER')
            build_info['commit_sha'] = os.environ.get('BITBUCKET_COMMIT')
            
            # Construct build URL
            workspace = os.environ.get('BITBUCKET_WORKSPACE')
            repo_slug = os.environ.get('BITBUCKET_REPO_SLUG')
            build_num = build_info['build_number']
            if workspace and repo_slug and build_num:
                build_info['build_url'] = f"https://bitbucket.org/{workspace}/{repo_slug}/pipelines/results/{build_num}"
        
        # Generic CI fallback
        if not build_info.get('commit_sha'):
            build_info['commit_sha'] = (
                os.environ.get('GIT_COMMIT') or
                os.environ.get('COMMIT_SHA') or
                os.environ.get('SHA')
            )
        
        if not build_info.get('build_id'):
            build_info['build_id'] = (
                os.environ.get('BUILD_ID') or
                os.environ.get('CI_BUILD_ID')
            )
        
        if not build_info['build_url']:
            build_info['build_url'] = os.environ.get('BUILD_URL')
        
        # Clean up None values
        return {k: v for k, v in build_info.items() if v is not None}
    
    def _extract_repository_info(self):
        """Extract repository information."""
        repo_info = {
            'name': None,
            'owner': None,
            'url': None
        }
        
        if self.ci_provider == 'github_actions':
            repository = os.environ.get('GITHUB_REPOSITORY', '')
            if '/' in repository:
                parts = repository.split('/', 1)
                repo_info['owner'] = parts[0]
                repo_info['name'] = parts[1]
            
            server_url = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
            if repository:
                repo_info['url'] = f"{server_url}/{repository}"
                
        elif self.ci_provider == 'bitbucket_pipelines':
            repo_info['name'] = os.environ.get('BITBUCKET_REPO_SLUG')
            repo_info['owner'] = os.environ.get('BITBUCKET_WORKSPACE')
            
            if repo_info['owner'] and repo_info['name']:
                repo_info['url'] = f"https://bitbucket.org/{repo_info['owner']}/{repo_info['name']}"
        
        # Generic fallback
        if not repo_info['url']:
            repo_info['url'] = os.environ.get('REPO_URL')
        
        # Clean up None values
        return {k: v for k, v in repo_info.items() if v is not None}
    
    def _log_extracted_info(self):
        """Log extracted CI information in debug mode."""
        logger.debug("=" * 60)
        logger.debug("CI/CD Environment Information Extraction")
        logger.debug("=" * 60)
        
        logger.debug(f"CI Provider: {self.ci_provider or 'Not detected'}")
        
        if self.pr_info:
            logger.debug("\nPR Information:")
            for key, value in self.pr_info.items():
                logger.debug(f"  {key}: {value}")
        else:
            logger.debug("\nPR Information: No PR context detected")
        
        if self.build_info:
            logger.debug("\nBuild Information:")
            for key, value in self.build_info.items():
                logger.debug(f"  {key}: {value}")
        else:
            logger.debug("\nBuild Information: Not available")
        
        if self.repository_info:
            logger.debug("\nRepository Information:")
            for key, value in self.repository_info.items():
                logger.debug(f"  {key}: {value}")
        else:
            logger.debug("\nRepository Information: Not available")
        
        logger.debug("=" * 60)
    
    def get_metadata(self):
        """Get all CI metadata as a dictionary."""
        metadata = {}
        
        if self.ci_provider:
            metadata['ci_provider'] = self.ci_provider
        
        if self.pr_info:
            metadata['pr'] = self.pr_info
        
        if self.build_info:
            metadata['build'] = self.build_info
        
        if self.repository_info:
            metadata['repository'] = self.repository_info
        
        return metadata if metadata else None
    
    def get_pr_context_string(self):
        """Get a human-readable PR context string."""
        if not self.pr_info:
            return None
        
        parts = []
        
        if 'number' in self.pr_info:
            parts.append(f"PR #{self.pr_info['number']}")
        
        if 'source_branch' in self.pr_info and 'target_branch' in self.pr_info:
            parts.append(f"{self.pr_info['source_branch']} → {self.pr_info['target_branch']}")
        elif 'source_branch' in self.pr_info:
            parts.append(f"branch: {self.pr_info['source_branch']}")
        
        if 'author' in self.pr_info:
            parts.append(f"by {self.pr_info['author']}")
        
        return " ".join(parts) if parts else None
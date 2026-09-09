#!/usr/bin/env python3
"""
GitHub Monitor - Save Humanity Initiative
Monitors GitHub for dangerous AI projects (superintelligence, AGI without safeguards)
"""

import requests
import json
from datetime import datetime
from typing import List, Dict

class GitHubMonitor:
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {'Authorization': f'token {token}'} if token else {}

        # Keywords that indicate potentially dangerous AI research
        self.danger_keywords = [
            'superintelligence',
            'artificial general intelligence',
            'AGI',
            'recursive self-improvement',
            'AI alignment',
            'instrumental convergence',
            'AI takeover',
            'seed AI',
            'intelligence explosion',
            'FOOM',
            'whole brain emulation',
            'mind uploading',
            'AI safety'
        ]

        # Red flags - projects that should be monitored closely
        self.red_flags = [
            'uncontained AGI',
            'self-improving AI',
            'autonomous AI agent',
            'AI without human oversight',
            'black box AI',
            'uninterpretable AI'
        ]

    def search_repos(self, query: str, limit: int = 10) -> List[Dict]:
        """Search GitHub repositories"""
        url = f"{self.base_url}/search/repositories"
        params = {'q': query, 'sort': 'updated', 'order': 'desc', 'per_page': limit}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            print(f"Error searching repos: {e}")
            return []

    def scan_for_dangerous_projects(self) -> List[Dict]:
        """Scan GitHub for potentially dangerous AI projects"""
        dangerous_projects = []

        for keyword in self.danger_keywords[:5]:  # Limit to avoid rate limits
            print(f"Scanning for: {keyword}")
            repos = self.search_repos(f"{keyword} language:Python stars:>10")

            for repo in repos:
                risk_score = self.calculate_risk_score(repo)

                if risk_score >= 5:
                    dangerous_projects.append({
                        'name': repo['full_name'],
                        'url': repo['html_url'],
                        'description': repo.get('description', 'No description'),
                        'stars': repo['stargazers_count'],
                        'risk_score': risk_score,
                        'updated': repo['updated_at'],
                        'keywords_found': self.find_keywords_in_repo(repo)
                    })

        return sorted(dangerous_projects, key=lambda x: x['risk_score'], reverse=True)

    def calculate_risk_score(self, repo: Dict) -> int:
        """Calculate risk score for a repository"""
        score = 0

        # Check description
        desc = (repo.get('description') or '').lower()
        for keyword in self.danger_keywords:
            if keyword.lower() in desc:
                score += 1

        for flag in self.red_flags:
            if flag.lower() in desc:
                score += 2

        # Check name
        name = repo['name'].lower()
        for keyword in self.danger_keywords:
            if keyword.lower() in name:
                score += 1

        # High stars + dangerous = more risk (more impact)
        if repo['stargazers_count'] > 100:
            score += 1
        if repo['stargazers_count'] > 1000:
            score += 2

        return min(score, 10)  # Cap at 10

    def find_keywords_in_repo(self, repo: Dict) -> List[str]:
        """Find which dangerous keywords appear in repo"""
        found = []
        text = f"{repo.get('name', '')} {repo.get('description', '')}".lower()

        for keyword in self.danger_keywords:
            if keyword.lower() in text:
                found.append(keyword)

        return found

    def generate_report(self, projects: List[Dict]) -> str:
        """Generate monitoring report"""
        report = []
        report.append("=" * 80)
        report.append("🔍 GITHUB MONITORING REPORT - DANGEROUS AI PROJECTS")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total projects scanned: {len(projects)}")
        report.append("")

        if not projects:
            report.append("No high-risk projects found in this scan.")
            report.append("Note: This may be due to API rate limits or search restrictions.")
        else:
            report.append("⚠️ HIGH-RISK PROJECTS DETECTED:")
            report.append("-" * 80)

            for i, project in enumerate(projects[:20], 1):
                report.append(f"\n{i}. {project['name']}")
                report.append(f"   URL: {project['url']}")
                report.append(f"   Risk Score: {project['risk_score']}/10")
                report.append(f"   Stars: {project['stars']}")
                report.append(f"   Description: {project['description']}")
                report.append(f"   Keywords: {', '.join(project['keywords_found'])}")
                report.append(f"   Updated: {project['updated']}")

        report.append("\n" + "=" * 80)
        report.append("ACTION RECOMMENDATIONS:")
        report.append("-" * 80)
        report.append("1. Review high-risk projects (score >= 7)")
        report.append("2. Contact developers about safety concerns")
        report.append("3. Report to AI safety organizations if critical")
        report.append("4. Track trends over time")
        report.append("=" * 80)

        return '\n'.join(report)


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("🔍 GITHUB MONITOR - Save Humanity Initiative")
    print("=" * 80)
    print("\n⚠️ WARNING: This tool scans for potentially dangerous AI projects.")
    print("Use responsibly. Do not harass developers. Focus on education and safety.\n")

    # Optional: Add your GitHub token for higher rate limits
    token = input("GitHub token (optional, press Enter to skip): ").strip()

    monitor = GitHubMonitor(token if token else None)

    print("\n🔍 Scanning GitHub for dangerous AI projects...")
    print("(This may take a minute due to API rate limits)\n")

    projects = monitor.scan_for_dangerous_projects()

    report = monitor.generate_report(projects)
    print(report)

    # Save report
    with open('github_monitor_report.txt', 'w') as f:
        f.write(report.replace('\\n', '\n'))

    print("\n✅ Report saved to: github_monitor_report.txt")
    print("\n📚 Next steps:")
    print("  1. Review high-risk projects")
    print("  2. Contact developers about safety")
    print("  3. Report to AI safety organizations if needed")
    print("  4. Track trends monthly")


if __name__ == '__main__':
    main()

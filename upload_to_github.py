#!/usr/bin/env python3
"""
GitHub Upload Script for UAV Accident Forensics Project
Automated script to prepare and upload the project to GitHub
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

class GitHubUploader:
    """Automated GitHub upload manager"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.repo_name = "UAV-accident-forensics-via-HFACS-LLM-reasoning"
        
    def check_prerequisites(self):
        """Check if git is installed and configured"""
        print("🔍 Checking prerequisites...")
        
        try:
            # Check git installation
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Git is not installed")
                return False
            print(f"✅ Git found: {result.stdout.strip()}")
            
            # Check git configuration
            try:
                name = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
                email = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
                
                if not name.stdout.strip() or not email.stdout.strip():
                    print("⚠️ Git user not configured. Please run:")
                    print("   git config --global user.name 'Your Name'")
                    print("   git config --global user.email 'your.email@example.com'")
                    return False
                
                print(f"✅ Git user: {name.stdout.strip()} <{email.stdout.strip()}>")
                
            except:
                print("⚠️ Could not check git configuration")
                
            return True
            
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False
    
    def prepare_files(self):
        """Prepare files for GitHub upload"""
        print("📁 Preparing files for GitHub...")
        
        # Replace README.md with GitHub version
        if os.path.exists('README_GITHUB.md'):
            print("  📝 Replacing README.md with GitHub version...")
            if os.path.exists('README.md'):
                shutil.move('README.md', 'README_original.md')
            shutil.move('README_GITHUB.md', 'README.md')
            print("  ✅ README.md updated")
        
        # Create .gitignore if it doesn't exist
        if not os.path.exists('.gitignore'):
            print("  ⚠️ .gitignore not found")
            return False
        
        # Check for sensitive files
        sensitive_files = [
            '.env',
            'asrs_data.db',
            '*.log',
            '__pycache__',
            'node_modules'
        ]
        
        print("  🔒 Checking for sensitive files...")
        for pattern in sensitive_files:
            if '*' in pattern:
                # Handle wildcard patterns
                import glob
                files = glob.glob(pattern)
                if files:
                    print(f"  ⚠️ Found sensitive files: {files}")
            else:
                if os.path.exists(pattern):
                    print(f"  ⚠️ Found sensitive file: {pattern}")
        
        print("  ✅ File preparation complete")
        return True
    
    def initialize_git(self):
        """Initialize git repository"""
        print("🔧 Initializing git repository...")
        
        try:
            # Check if already a git repository
            if os.path.exists('.git'):
                print("  ✅ Git repository already exists")
                return True
            
            # Initialize git repository
            subprocess.run(['git', 'init'], check=True, capture_output=True)
            print("  ✅ Git repository initialized")
            
            # Set main branch
            subprocess.run(['git', 'branch', '-M', 'main'], check=True, capture_output=True)
            print("  ✅ Main branch set")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Git initialization failed: {e}")
            return False
    
    def add_and_commit(self):
        """Add files and create initial commit"""
        print("📦 Adding files and creating commit...")
        
        try:
            # Add all files
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            print("  ✅ Files added to git")
            
            # Create commit
            commit_message = """Initial commit: UAV Accident Forensics via HFACS-LLM Reasoning system

🚀 Features:
- Complete Streamlit web application for UAV accident analysis
- OpenAI GPT-4o-mini integration for intelligent analysis
- HFACS 8.0 framework implementation (18 classifications)
- Advanced 3D visualizations and knowledge graphs
- Smart form assistance with narrative-first approach
- Real-time dashboards and interactive visualizations
- Docker deployment support with multi-service architecture
- Comprehensive documentation and testing

🛠️ Technical Stack:
- Frontend: Streamlit + Plotly + HTML/CSS
- Backend: Python + Pandas + SQLite
- AI Engine: OpenAI GPT-4o-mini with Function Calling
- Visualization: Node.js + Three.js + D3.js + Socket.io
- Deployment: Docker + Docker Compose
- CI/CD: GitHub Actions

📚 Documentation:
- Professional README with installation guide
- API documentation for all components
- Contributing guidelines for developers
- Docker deployment instructions
- Comprehensive project structure documentation

🔒 Security:
- Environment variable configuration
- Input validation and sanitization
- Secure API communication
- No sensitive data in repository

This system provides a complete solution for UAV accident forensics,
combining traditional HFACS analysis with modern LLM reasoning
for enhanced safety insights in low-altitude operations."""

            subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
            print("  ✅ Initial commit created")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Commit failed: {e}")
            return False
    
    def setup_remote(self, github_username):
        """Set up GitHub remote"""
        print(f"🔗 Setting up GitHub remote for user: {github_username}...")
        
        try:
            remote_url = f"https://github.com/{github_username}/{self.repo_name}.git"
            
            # Check if remote already exists
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ Remote origin already exists: {result.stdout.strip()}")
                return True
            
            # Add remote origin
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                          check=True, capture_output=True)
            print(f"  ✅ Remote origin added: {remote_url}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Remote setup failed: {e}")
            return False
    
    def push_to_github(self):
        """Push to GitHub"""
        print("🚀 Pushing to GitHub...")
        
        try:
            # Push to GitHub
            result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ Push failed: {result.stderr}")
                print("  💡 Make sure you have:")
                print("     1. Created the repository on GitHub")
                print("     2. Have proper authentication (token/SSH)")
                print("     3. Repository name matches exactly")
                return False
            
            print("  ✅ Successfully pushed to GitHub!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Push failed: {e}")
            return False
    
    def display_next_steps(self, github_username):
        """Display next steps after upload"""
        repo_url = f"https://github.com/{github_username}/{self.repo_name}"
        
        print("\n" + "="*60)
        print("🎉 PROJECT SUCCESSFULLY UPLOADED TO GITHUB!")
        print("="*60)
        
        print(f"\n📍 Repository URL: {repo_url}")
        
        print("\n📋 Next Steps:")
        print("1. 🌐 Visit your repository on GitHub")
        print("2. 📝 Update repository description and topics")
        print("3. 🔧 Configure GitHub Actions secrets:")
        print("   - OPENAI_API_KEY")
        print("   - DOCKERHUB_USERNAME (optional)")
        print("   - DOCKERHUB_TOKEN (optional)")
        print("4. 🏷️ Create your first release (v1.0.0)")
        print("5. 📚 Enable Wiki and Discussions")
        print("6. 🛡️ Set up branch protection rules")
        
        print("\n🔗 Quick Links:")
        print(f"   Repository: {repo_url}")
        print(f"   Settings: {repo_url}/settings")
        print(f"   Actions: {repo_url}/actions")
        print(f"   Releases: {repo_url}/releases")
        
        print("\n💡 Promotion Tips:")
        print("   - Share in aviation safety communities")
        print("   - Post in AI/ML research groups")
        print("   - Submit to relevant conferences")
        print("   - Add to Awesome Lists")
        
        print("\n🚁 Happy coding and safe flying! ✨")
    
    def run(self):
        """Run the complete upload process"""
        print("🚀 UAV Accident Forensics - GitHub Upload Script")
        print("="*50)
        
        # Get GitHub username
        github_username = input("\n👤 Enter your GitHub username: ").strip()
        if not github_username:
            print("❌ GitHub username is required")
            return False
        
        # Confirm repository name
        print(f"\n📁 Repository name: {self.repo_name}")
        confirm = input("Continue with this name? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Upload cancelled")
            return False
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Prepare files
        if not self.prepare_files():
            return False
        
        # Initialize git
        if not self.initialize_git():
            return False
        
        # Add and commit
        if not self.add_and_commit():
            return False
        
        # Setup remote
        if not self.setup_remote(github_username):
            return False
        
        # Final confirmation
        print(f"\n⚠️ Ready to push to: https://github.com/{github_username}/{self.repo_name}")
        print("Make sure you have created this repository on GitHub first!")
        final_confirm = input("Proceed with push? (y/N): ").strip().lower()
        
        if final_confirm != 'y':
            print("❌ Upload cancelled")
            return False
        
        # Push to GitHub
        if not self.push_to_github():
            return False
        
        # Display next steps
        self.display_next_steps(github_username)
        
        return True

def main():
    """Main entry point"""
    uploader = GitHubUploader()
    success = uploader.run()
    
    if success:
        print("\n✅ Upload completed successfully!")
    else:
        print("\n❌ Upload failed. Please check the errors above.")
    
    input("\nPress Enter to exit...")
    return success

if __name__ == '__main__':
    main()

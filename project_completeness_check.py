#!/usr/bin/env python3
"""
Project Completeness Check for GitHub Upload
Comprehensive validation of project files and structure
"""

import os
import json
from pathlib import Path

class ProjectChecker:
    """Project completeness and quality checker"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check_file_exists(self, filepath, description, required=True):
        """Check if a file exists"""
        self.total_checks += 1
        if os.path.exists(filepath):
            print(f"✅ {description}: {filepath}")
            self.success_count += 1
            return True
        else:
            if required:
                self.issues.append(f"Missing required file: {filepath}")
                print(f"❌ {description}: {filepath} (MISSING)")
            else:
                self.warnings.append(f"Optional file missing: {filepath}")
                print(f"⚠️ {description}: {filepath} (OPTIONAL)")
            return False
    
    def check_directory_exists(self, dirpath, description, required=True):
        """Check if a directory exists"""
        self.total_checks += 1
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            print(f"✅ {description}: {dirpath}/")
            self.success_count += 1
            return True
        else:
            if required:
                self.issues.append(f"Missing required directory: {dirpath}")
                print(f"❌ {description}: {dirpath}/ (MISSING)")
            else:
                self.warnings.append(f"Optional directory missing: {dirpath}")
                print(f"⚠️ {description}: {dirpath}/ (OPTIONAL)")
            return False
    
    def check_file_content(self, filepath, required_content, description):
        """Check if file contains required content"""
        self.total_checks += 1
        if not os.path.exists(filepath):
            self.issues.append(f"Cannot check content of missing file: {filepath}")
            print(f"❌ {description}: File missing")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for item in required_content:
                if item not in content:
                    self.issues.append(f"Missing content in {filepath}: {item}")
                    print(f"❌ {description}: Missing '{item}'")
                    return False
            
            print(f"✅ {description}: Content validated")
            self.success_count += 1
            return True
            
        except Exception as e:
            self.issues.append(f"Error reading {filepath}: {e}")
            print(f"❌ {description}: Read error")
            return False
    
    def check_core_files(self):
        """Check core project files"""
        print("\n📁 Checking Core Project Files...")
        
        # Essential files
        self.check_file_exists('README.md', 'Main README file')
        self.check_file_exists('LICENSE', 'License file')
        self.check_file_exists('requirements.txt', 'Python dependencies')
        self.check_file_exists('.gitignore', 'Git ignore rules')
        self.check_file_exists('setup.py', 'Package setup')
        
        # Documentation files
        self.check_file_exists('CONTRIBUTING.md', 'Contributing guidelines')
        self.check_file_exists('CHANGELOG.md', 'Version history')
        self.check_file_exists('PROJECT_STRUCTURE.md', 'Project structure')
        
        # Configuration files
        self.check_file_exists('.env.template', 'Environment template')
        self.check_file_exists('Dockerfile', 'Docker configuration')
        self.check_file_exists('docker-compose.yml', 'Docker Compose')
        
        # GitHub files
        self.check_file_exists('.github/workflows/ci.yml', 'CI/CD pipeline')
    
    def check_python_modules(self):
        """Check Python source files"""
        print("\n🐍 Checking Python Modules...")
        
        # Core modules
        modules = [
            ('streamlit_app.py', 'Main Streamlit application'),
            ('data_processor.py', 'Data processing utilities'),
            ('ai_analyzer.py', 'AI analysis engine'),
            ('hfacs_analyzer.py', 'HFACS analyzer'),
            ('smart_form_assistant.py', 'Smart form assistant'),
            ('advanced_visualizations.py', 'Advanced visualizations'),
            ('run.py', 'System launcher'),
        ]
        
        for filename, description in modules:
            self.check_file_exists(filename, description)
    
    def check_directories(self):
        """Check project directories"""
        print("\n📂 Checking Project Directories...")
        
        # Required directories
        self.check_directory_exists('data', 'Data directory')
        self.check_directory_exists('logs', 'Logs directory')
        self.check_directory_exists('reports', 'Reports directory')
        self.check_directory_exists('.github', 'GitHub configuration')
        self.check_directory_exists('.github/workflows', 'GitHub Actions')
        
        # Optional directories
        self.check_directory_exists('web_components', 'Node.js components', required=False)
        self.check_directory_exists('tests', 'Test files', required=False)
    
    def check_readme_content(self):
        """Check README.md content quality"""
        print("\n📖 Checking README Content...")
        
        required_sections = [
            '# UAV Accident Forensics',
            'Installation',
            'Usage',
            'Core Research Contributions',
            'License',
            'streamlit',
            'OpenAI',
            'HFACS'
        ]
        
        self.check_file_content('README.md', required_sections, 'README content')
    
    def check_requirements_content(self):
        """Check requirements.txt content"""
        print("\n📦 Checking Requirements Content...")
        
        required_packages = [
            'streamlit',
            'pandas',
            'numpy',
            'openai',
            'plotly'
        ]
        
        self.check_file_content('requirements.txt', required_packages, 'Requirements content')
    
    def check_gitignore_content(self):
        """Check .gitignore content"""
        print("\n🚫 Checking .gitignore Content...")
        
        required_patterns = [
            '__pycache__',
            '*.pyc',
            '.env',
            '*.db',
            '*.log',
            'node_modules'
        ]
        
        self.check_file_content('.gitignore', required_patterns, '.gitignore content')
    
    def check_sensitive_files(self):
        """Check for sensitive files that shouldn't be committed"""
        print("\n🔒 Checking for Sensitive Files...")
        
        sensitive_files = [
            '.env',
            'asrs_data.db',
            'config.ini',
            'secrets.json',
            'api_keys.txt'
        ]
        
        for filepath in sensitive_files:
            self.total_checks += 1
            if os.path.exists(filepath):
                self.issues.append(f"Sensitive file found: {filepath}")
                print(f"❌ Sensitive file detected: {filepath}")
            else:
                print(f"✅ No sensitive file: {filepath}")
                self.success_count += 1
    
    def check_file_sizes(self):
        """Check for large files that might cause issues"""
        print("\n📏 Checking File Sizes...")
        
        max_size_mb = 100  # GitHub file size limit
        large_files = []
        
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    if size_mb > max_size_mb:
                        large_files.append((filepath, size_mb))
                except:
                    pass
        
        self.total_checks += 1
        if large_files:
            for filepath, size_mb in large_files:
                self.warnings.append(f"Large file: {filepath} ({size_mb:.1f}MB)")
                print(f"⚠️ Large file: {filepath} ({size_mb:.1f}MB)")
        else:
            print("✅ No large files detected")
            self.success_count += 1
    
    def check_python_syntax(self):
        """Check Python files for syntax errors"""
        print("\n🔍 Checking Python Syntax...")
        
        python_files = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        syntax_errors = []
        for filepath in python_files:
            self.total_checks += 1
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    compile(f.read(), filepath, 'exec')
                print(f"✅ Syntax OK: {filepath}")
                self.success_count += 1
            except SyntaxError as e:
                syntax_errors.append((filepath, str(e)))
                print(f"❌ Syntax Error: {filepath}")
            except Exception as e:
                self.warnings.append(f"Could not check syntax: {filepath} - {e}")
                print(f"⚠️ Could not check: {filepath}")
        
        if syntax_errors:
            for filepath, error in syntax_errors:
                self.issues.append(f"Syntax error in {filepath}: {error}")
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("📊 PROJECT COMPLETENESS REPORT")
        print("="*60)
        
        success_rate = (self.success_count / self.total_checks * 100) if self.total_checks > 0 else 0
        
        print(f"\n📈 Overall Score: {self.success_count}/{self.total_checks} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT - Project is ready for GitHub!")
        elif success_rate >= 75:
            print("✅ GOOD - Project is mostly ready, minor issues to fix")
        elif success_rate >= 50:
            print("⚠️ FAIR - Several issues need attention")
        else:
            print("❌ POOR - Major issues need to be resolved")
        
        if self.issues:
            print(f"\n❌ Critical Issues ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if not self.issues and not self.warnings:
            print("\n🎉 No issues found! Project is ready for upload.")
        
        print("\n📋 Next Steps:")
        if self.issues:
            print("   1. Fix all critical issues listed above")
            print("   2. Re-run this check")
            print("   3. Upload to GitHub when all issues are resolved")
        else:
            print("   1. Run: python upload_to_github.py")
            print("   2. Create repository on GitHub")
            print("   3. Configure repository settings")
            print("   4. Set up GitHub Actions secrets")
        
        return len(self.issues) == 0
    
    def run_all_checks(self):
        """Run all project checks"""
        print("🔍 UAV Accident Forensics - Project Completeness Check")
        print("="*55)
        
        self.check_core_files()
        self.check_python_modules()
        self.check_directories()
        self.check_readme_content()
        self.check_requirements_content()
        self.check_gitignore_content()
        self.check_sensitive_files()
        self.check_file_sizes()
        self.check_python_syntax()
        
        return self.generate_report()

def main():
    """Main entry point"""
    checker = ProjectChecker()
    ready = checker.run_all_checks()
    
    if ready:
        print("\n✅ Project is ready for GitHub upload!")
        upload = input("\nWould you like to run the upload script now? (y/N): ").strip().lower()
        if upload == 'y':
            try:
                import subprocess
                subprocess.run([sys.executable, 'upload_to_github.py'])
            except Exception as e:
                print(f"Could not run upload script: {e}")
                print("Please run manually: python upload_to_github.py")
    else:
        print("\n❌ Please fix the issues above before uploading to GitHub.")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    import sys
    main()

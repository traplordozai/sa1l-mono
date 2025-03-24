#!/usr/bin/env python
import os
import sys
import subprocess
import django
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

def ensure_environment_variables():
    """Ensure all required environment variables are set"""
    required_vars = {
        'DJANGO_SETTINGS_MODULE': 'sail_backend.test_settings',
        'SECRET_KEY': 'test-secret-key',
        'DEBUG': 'False',
        'DATABASE_URL': 'sqlite:///:memory:',
        'REDIS_URL': 'redis://localhost:6379/0',
        'OPENROUTER_API_KEY': 'test-key',
        'ALLOWED_HOSTS': '*'
    }
    
    for var, default_value in required_vars.items():
        if var not in os.environ:
            os.environ[var] = default_value
            print(f"Setting {var} to default value: {default_value}")

def setup_django():
    """Set up Django with the correct settings"""
    try:
        # Ensure environment variables are set
        ensure_environment_variables()
        
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sail_backend.test_settings')
        django.setup()
        
        from django.conf import settings
        return settings
    except Exception as e:
        print(f"Error setting up Django: {str(e)}")
        sys.exit(1)

def run_security_checks():
    """Run security-related checks"""
    print("Running security checks...")
    try:
        from django.core.management import call_command
        # Run Django's built-in security checks
        call_command('check', '--deploy')
        print("✓ Security checks passed")
    except Exception as e:
        print("✗ Security checks failed:", str(e))
        return False
    return True

def run_tests():
    """Run all tests"""
    print("Running tests...")
    try:
        from django.test.runner import DiscoverRunner
        test_runner = DiscoverRunner()
        failures = test_runner.run_tests(['students', 'config'])
        if failures:
            print("✗ Tests failed")
            return False
        print("✓ Tests passed")
        return True
    except Exception as e:
        print("✗ Tests failed with error:", str(e))
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("Checking dependencies...")
    try:
        requirements_file = project_root / 'requirements.txt'
        if not requirements_file.exists():
            print("✗ requirements.txt not found")
            return False
            
        # Try using pkg_resources first
        try:
            import pkg_resources
            with open(requirements_file) as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                pkg_resources.require(requirements)
        except ImportError:
            # Fallback to pip if pkg_resources is not available
            try:
                import pip
                subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
            except Exception as e:
                print("✗ Dependencies check failed:", str(e))
                return False
        
        print("✓ Dependencies check passed")
        return True
    except Exception as e:
        print("✗ Dependencies check failed:", str(e))
        return False

def check_database():
    """Check database configuration and migrations"""
    print("Checking database...")
    try:
        from django.core.management import call_command
        # Check if migrations are up to date
        call_command('showmigrations', '--list')
        # Check database connection
        call_command('check')
        print("✓ Database check passed")
        return True
    except Exception as e:
        print("✗ Database check failed:", str(e))
        return False

def check_settings():
    """Check production settings"""
    print("Checking settings...")
    try:
        from django.conf import settings
        required_settings = [
            'SECRET_KEY',
            'DEBUG',
            'ALLOWED_HOSTS',
            'DATABASES',
            'CACHES',
            'LOGGING',
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print("✗ Missing required settings:", ', '.join(missing_settings))
            return False
        
        if settings.DEBUG:
            print("✗ DEBUG is set to True in production settings")
            return False
        
        print("✓ Settings check passed")
        return True
    except Exception as e:
        print("✗ Settings check failed:", str(e))
        return False

def check_environment():
    """Check environment variables"""
    print("Checking environment variables...")
    required_vars = [
        'DJANGO_SETTINGS_MODULE',
        'SECRET_KEY',
        'DEBUG',
        'DATABASE_URL',
        'REDIS_URL',
        'OPENROUTER_API_KEY',
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)
    
    if missing_vars:
        print("✗ Missing required environment variables:", ', '.join(missing_vars))
        return False
    
    print("✓ Environment variables check passed")
    return True

def main():
    """Main function to run all checks"""
    try:
        # Set up Django first
        settings = setup_django()
        
        checks = [
            ("Environment", check_environment),
            ("Security", run_security_checks),
            ("Tests", run_tests),
            ("Dependencies", check_dependencies),
            ("Database", check_database),
            ("Settings", check_settings),
        ]
        
        all_passed = True
        for name, check in checks:
            print(f"\nRunning {name} check...")
            if not check():
                all_passed = False
                print(f"✗ {name} check failed")
            else:
                print(f"✓ {name} check passed")
        
        if all_passed:
            print("\n✓ All checks passed! Ready for deployment.")
        else:
            print("\n✗ Some checks failed. Please fix the issues before deploying.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
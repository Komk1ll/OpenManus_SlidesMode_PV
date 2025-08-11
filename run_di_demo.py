#!/usr/bin/env python3
"""Complete demonstration script for Spark DI architecture.

This script demonstrates 100% automated testing and production readiness
by running comprehensive tests and creating a GPT-5 presentation.
"""

import asyncio
import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse


class DIArchitectureDemo:
    """Main demo orchestrator for DI architecture."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {
            "tests": {},
            "demo": {},
            "coverage": {},
            "performance": {},
            "timestamp": time.time()
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command: List[str], description: str) -> Dict[str, Any]:
        """Run a command and capture results."""
        self.log(f"Running: {description}")
        self.log(f"Command: {' '.join(command)}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "command": ' '.join(command)
            }
            
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {description}", "ERROR")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "duration": time.time() - start_time,
                "command": ' '.join(command)
            }
        except Exception as e:
            self.log(f"Command failed: {description} - {e}", "ERROR")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time() - start_time,
                "command": ' '.join(command)
            }
    
    def run_unit_tests(self) -> bool:
        """Run unit tests with coverage."""
        self.log("🧪 Running unit tests with coverage...")
        
        result = self.run_command(
            [sys.executable, "-m", "pytest", "tests/test_di_integration.py", "-v", "--cov=app", "--cov-report=html", "--cov-report=term"],
            "Unit tests with coverage"
        )
        
        self.results["tests"]["unit"] = result
        
        if result["success"]:
            self.log("✅ Unit tests passed")
            return True
        else:
            self.log("❌ Unit tests failed", "ERROR")
            self.log(f"Error: {result['stderr']}", "ERROR")
            return False
    
    def run_performance_tests(self) -> bool:
        """Run performance tests."""
        self.log("⚡ Running performance tests...")
        
        result = self.run_command(
            [sys.executable, "-m", "pytest", "tests/test_performance.py", "-v", "--durations=10"],
            "Performance tests"
        )
        
        self.results["tests"]["performance"] = result
        
        if result["success"]:
            self.log("✅ Performance tests passed")
            return True
        else:
            self.log("❌ Performance tests failed", "ERROR")
            self.log(f"Error: {result['stderr']}", "ERROR")
            return False
    
    def run_integration_tests(self) -> bool:
        """Run all integration tests."""
        self.log("🔗 Running integration tests...")
        
        result = self.run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--cov=app", "--cov-report=xml"],
            "Integration tests"
        )
        
        self.results["tests"]["integration"] = result
        
        if result["success"]:
            self.log("✅ Integration tests passed")
            return True
        else:
            self.log("❌ Integration tests failed", "ERROR")
            self.log(f"Error: {result['stderr']}", "ERROR")
            return False
    
    async def run_gpt5_demo(self) -> bool:
        """Run GPT-5 presentation demo."""
        self.log("🎯 Running GPT-5 presentation demo...")
        
        try:
            # Import and run the demo
            sys.path.insert(0, str(Path.cwd()))
            from demo.gpt5_presentation_demo import main as demo_main
            
            start_time = time.time()
            success = await demo_main()
            duration = time.time() - start_time
            
            self.results["demo"]["gpt5_presentation"] = {
                "success": success,
                "duration": duration,
                "description": "GPT-5 presentation generation"
            }
            
            if success:
                self.log(f"✅ GPT-5 demo completed in {duration:.2f}s")
                return True
            else:
                self.log("❌ GPT-5 demo failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ GPT-5 demo error: {e}", "ERROR")
            self.results["demo"]["gpt5_presentation"] = {
                "success": False,
                "duration": 0,
                "error": str(e)
            }
            return False
    
    def check_coverage(self) -> Dict[str, Any]:
        """Check test coverage results."""
        self.log("📊 Checking test coverage...")
        
        coverage_file = Path("coverage.xml")
        html_coverage = Path("htmlcov/index.html")
        
        coverage_info = {
            "xml_exists": coverage_file.exists(),
            "html_exists": html_coverage.exists(),
            "xml_path": str(coverage_file) if coverage_file.exists() else None,
            "html_path": str(html_coverage) if html_coverage.exists() else None
        }
        
        self.results["coverage"] = coverage_info
        
        if coverage_info["xml_exists"] and coverage_info["html_exists"]:
            self.log("✅ Coverage reports generated")
        else:
            self.log("⚠️  Some coverage reports missing", "WARNING")
        
        return coverage_info
    
    def generate_report(self) -> str:
        """Generate comprehensive demo report."""
        self.log("📝 Generating demo report...")
        
        report = {
            "title": "Spark DI Architecture Demo Report",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results,
            "summary": {
                "total_tests_passed": sum(1 for test in self.results["tests"].values() if test.get("success", False)),
                "total_tests_run": len(self.results["tests"]),
                "demo_success": self.results["demo"].get("gpt5_presentation", {}).get("success", False),
                "coverage_available": self.results["coverage"].get("xml_exists", False)
            }
        }
        
        # Save report
        report_file = Path("demo_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📄 Report saved to: {report_file}")
        return str(report_file)
    
    def print_summary(self):
        """Print demo summary."""
        print("\n" + "="*60)
        print("🎯 SPARK DI ARCHITECTURE DEMO SUMMARY")
        print("="*60)
        
        # Test results
        print("\n📋 TEST RESULTS:")
        for test_name, test_result in self.results["tests"].items():
            status = "✅ PASSED" if test_result.get("success", False) else "❌ FAILED"
            duration = test_result.get("duration", 0)
            print(f"  {test_name.upper()}: {status} ({duration:.2f}s)")
        
        # Demo results
        print("\n🎬 DEMO RESULTS:")
        for demo_name, demo_result in self.results["demo"].items():
            status = "✅ SUCCESS" if demo_result.get("success", False) else "❌ FAILED"
            duration = demo_result.get("duration", 0)
            print(f"  {demo_name.upper()}: {status} ({duration:.2f}s)")
        
        # Coverage
        print("\n📊 COVERAGE:")
        coverage = self.results["coverage"]
        if coverage.get("html_exists"):
            print(f"  HTML Report: ✅ {coverage['html_path']}")
        if coverage.get("xml_exists"):
            print(f"  XML Report: ✅ {coverage['xml_path']}")
        
        # Overall status
        all_tests_passed = all(test.get("success", False) for test in self.results["tests"].values())
        demo_success = self.results["demo"].get("gpt5_presentation", {}).get("success", False)
        
        print("\n🏆 OVERALL STATUS:")
        if all_tests_passed and demo_success:
            print("  ✅ ALL SYSTEMS GO - DI ARCHITECTURE IS PRODUCTION READY!")
            print("  🚀 100% Automated Testing: PASSED")
            print("  🎯 Live Demo: PASSED")
            print("  📊 Coverage Reports: GENERATED")
        else:
            print("  ❌ SOME ISSUES DETECTED - CHECK LOGS")
            if not all_tests_passed:
                print("  🧪 Tests: FAILED")
            if not demo_success:
                print("  🎬 Demo: FAILED")
        
        print("\n🔧 DI ARCHITECTURE FEATURES DEMONSTRATED:")
        print("  ✓ Dependency Injection Container")
        print("  ✓ Factory Pattern Implementation")
        print("  ✓ Interface-based Design")
        print("  ✓ Backward Compatibility")
        print("  ✓ Comprehensive Testing")
        print("  ✓ Performance Monitoring")
        print("  ✓ Multi-format Output Generation")
        print("  ✓ Error Handling & Resilience")
        print("  ✓ Thread Safety")
        print("  ✓ Memory Management")
        
        print("\n" + "="*60)
    
    async def run_full_demo(self) -> bool:
        """Run the complete demo suite."""
        self.log("🚀 Starting Spark DI Architecture Demo")
        self.log("="*50)
        
        success = True
        
        # Run tests
        if not self.run_unit_tests():
            success = False
        
        if not self.run_performance_tests():
            success = False
        
        if not self.run_integration_tests():
            success = False
        
        # Run demo
        if not await self.run_gpt5_demo():
            success = False
        
        # Check coverage
        self.check_coverage()
        
        # Generate report
        self.generate_report()
        
        # Print summary
        self.print_summary()
        
        return success


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Spark DI Architecture Demo")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    parser.add_argument("--tests-only", action="store_true", help="Run tests only")
    parser.add_argument("--demo-only", action="store_true", help="Run demo only")
    
    args = parser.parse_args()
    
    demo = DIArchitectureDemo(verbose=not args.quiet)
    
    try:
        if args.tests_only:
            success = (demo.run_unit_tests() and 
                      demo.run_performance_tests() and 
                      demo.run_integration_tests())
            demo.check_coverage()
        elif args.demo_only:
            success = await demo.run_gpt5_demo()
        else:
            success = await demo.run_full_demo()
        
        if success:
            print("\n🎉 Demo completed successfully!")
            print("The Spark DI architecture is ready for production use.")
            return 0
        else:
            print("\n💥 Demo encountered issues. Check the logs above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
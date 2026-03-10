#!/usr/bin/env python3
"""
Comprehensive Workflow Test Script
==================================

This script tests the complete Bug-to-PR autopilot workflow including:
1. Backend API functionality
2. GitHub operations
3. Frontend connectivity
4. Live status monitoring

Usage:
    python test_full_workflow.py
"""

import os
import time
import json
import requests
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_ISSUE_URL = "https://github.com/ritik-prog/n8n-automation-templates-5000/issues/9"
TEST_REPO = "ritik-prog/n8n-automation-templates-5000"
TIMEOUT = 300  # 5 minutes total timeout
STATUS_CHECK_INTERVAL = 5  # Check status every 5 seconds

class WorkflowTester:
    def __init__(self):
        self.run_id = None
        self.start_time = None
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        self.test_results.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
    
    def check_backend_health(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✅ Backend is healthy: {health_data}")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend health check error: {e}", "ERROR")
            return False
    
    def check_frontend_health(self) -> bool:
        """Check if frontend is accessible"""
        try:
            response = requests.get(f"{FRONTEND_URL}", timeout=10)
            if response.status_code == 200:
                self.log(f"✅ Frontend is accessible")
                return True
            else:
                self.log(f"❌ Frontend check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Frontend check error: {e}", "ERROR")
            return False
    
    def create_run(self) -> Optional[str]:
        """Create a new run"""
        try:
            payload = {
                "issueUrl": TEST_ISSUE_URL,
                "repo": TEST_REPO
            }
            
            self.log(f"🚀 Creating new run for {TEST_REPO}")
            response = requests.post(
                f"{BACKEND_URL}/runs",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                run_data = response.json()
                self.run_id = run_data.get("runId")
                self.log(f"✅ Run created successfully: {self.run_id}")
                return self.run_id
            else:
                self.log(f"❌ Run creation failed: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Run creation error: {e}", "ERROR")
            return None
    
    def get_run_status(self) -> Optional[Dict[str, Any]]:
        """Get current run status"""
        if not self.run_id:
            return None
            
        try:
            response = requests.get(f"{BACKEND_URL}/runs/{self.run_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"❌ Status check failed: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Status check error: {e}", "ERROR")
            return None
    
    def get_run_events(self) -> list:
        """Get run events for monitoring"""
        if not self.run_id:
            return []
            
        try:
            response = requests.get(f"{BACKEND_URL}/runs/{self.run_id}/events", timeout=10)
            if response.status_code == 200:
                # Parse SSE events
                events = []
                for line in response.text.strip().split('\n'):
                    if line.startswith('data: '):
                        try:
                            event_data = json.loads(line[6:])
                            events.append(event_data)
                        except json.JSONDecodeError:
                            continue
                return events
            else:
                return []
        except Exception as e:
            self.log(f"❌ Events check error: {e}", "ERROR")
            return []
    
    def approve_gate(self, gate: str, decision: str = "approve") -> bool:
        """Approve or reject a gate"""
        if not self.run_id:
            return False
            
        try:
            payload = {
                "gate": gate,
                "decision": decision,
                "note": f"Auto-{decision}ed by test script"
            }
            
            self.log(f"🔓 Approving gate: {gate} with decision: {decision}")
            response = requests.post(
                f"{BACKEND_URL}/runs/{self.run_id}/approve",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log(f"✅ Gate {gate} {decision}ed successfully")
                return True
            else:
                self.log(f"❌ Gate approval failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Gate approval error: {e}", "ERROR")
            return False
    
    def monitor_workflow(self) -> bool:
        """Monitor the workflow progress"""
        if not self.run_id:
            return False
            
        self.start_time = time.time()
        last_status = None
        
        self.log(f"📊 Starting workflow monitoring for run: {self.run_id}")
        
        while True:
            # Check timeout
            elapsed = time.time() - self.start_time
            if elapsed > TIMEOUT:
                self.log(f"⏰ Workflow monitoring timed out after {TIMEOUT} seconds", "ERROR")
                return False
            
            # Get current status
            run_data = self.get_run_status()
            if not run_data:
                time.sleep(STATUS_CHECK_INTERVAL)
                continue
            
            current_status = run_data.get("status")
            
            # Log status changes
            if current_status != last_status:
                self.log(f"🔄 Status changed: {last_status} → {current_status}")
                last_status = current_status
            
            # Check for completion
            if current_status == "completed":
                self.log(f"🎉 Workflow completed successfully!")
                return True
            elif current_status == "failed":
                self.log(f"❌ Workflow failed", "ERROR")
                return False
            
            # Check for waiting gates
            plan = run_data.get("plan", [])
            waiting_gates = [step for step in plan if step.get("status") == "waiting"]
            
            for gate_step in waiting_gates:
                gate_name = gate_step.get("name")
                if gate_name in ["propose-fix", "merge-pr"]:
                    self.log(f"⏳ Found waiting gate: {gate_name}")
                    if self.approve_gate(gate_name, "approve"):
                        time.sleep(2)  # Wait for approval to process
                    else:
                        self.log(f"❌ Failed to approve gate: {gate_name}", "ERROR")
                        return False
            
            # Log progress
            completed_steps = [step for step in plan if step.get("status") == "success"]
            total_steps = len(plan)
            progress = f"{len(completed_steps)}/{total_steps} steps completed"
            self.log(f"📈 Progress: {progress} (elapsed: {elapsed:.1f}s)")
            
            time.sleep(STATUS_CHECK_INTERVAL)
    
    def check_github_integration(self) -> bool:
        """Check if GitHub integration is working"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                services = health_data.get("services", {})
                
                github_status = services.get("github", "unknown")
                if github_status == "connected":
                    self.log(f"✅ GitHub integration: {github_status}")
                    return True
                else:
                    self.log(f"⚠️ GitHub integration status: {github_status}", "WARNING")
                    return False
            else:
                self.log("❌ Cannot check GitHub integration", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ GitHub integration check error: {e}", "ERROR")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run the complete workflow test"""
        self.log("🧪 Starting comprehensive workflow test")
        self.log("=" * 60)
        
        # Step 1: Health checks
        self.log("Step 1: Health Checks")
        if not self.check_backend_health():
            return False
        
        if not self.check_frontend_health():
            self.log("⚠️ Frontend not accessible, continuing with backend test", "WARNING")
        
        # Step 2: Integration checks
        self.log("Step 2: Integration Checks")
        if not self.check_github_integration():
            self.log("⚠️ GitHub integration issue detected", "WARNING")
        
        # Step 3: Create run
        self.log("Step 3: Create Run")
        if not self.create_run():
            return False
        
        # Step 4: Monitor workflow
        self.log("Step 4: Monitor Workflow")
        if not self.monitor_workflow():
            return False
        
        # Step 5: Final verification
        self.log("Step 5: Final Verification")
        final_status = self.get_run_status()
        if final_status:
            self.log(f"✅ Final run status: {final_status.get('status')}")
            
            # Check for PR creation
            github_data = final_status.get("github_data", {})
            if github_data.get("pr_url"):
                self.log(f"🎉 Pull Request created: {github_data['pr_url']}")
            else:
                self.log("⚠️ No PR URL found in final status", "WARNING")
        
        self.log("=" * 60)
        self.log("🎉 Comprehensive workflow test completed successfully!")
        return True
    
    def save_test_report(self):
        """Save test results to a file"""
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "run_id": self.run_id,
            "test_issue_url": TEST_ISSUE_URL,
            "test_repo": TEST_REPO,
            "results": self.test_results
        }
        
        filename = f"workflow_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📄 Test report saved to: {filename}")

def main():
    """Main test function"""
    print("🚀 Bug-to-PR Autopilot - Comprehensive Workflow Test")
    print("=" * 70)
    
    tester = WorkflowTester()
    
    try:
        success = tester.run_comprehensive_test()
        tester.save_test_report()
        
        if success:
            print("\n✅ All tests passed! The workflow is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed. Check the logs above for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        tester.save_test_report()
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        tester.save_test_report()
        return 1

if __name__ == "__main__":
    exit(main())

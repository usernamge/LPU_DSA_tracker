import subprocess
import time
import sys

def run_command(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def main():
    print("Auto Sync active. Checking for changes every 10 seconds...", flush=True)
    while True:
        try:
            # Check git status
            code, stdout, stderr = run_command(["git", "status", "--porcelain"])
            if code == 0 and stdout:
                # We want to filter out auto_sync.py changes if we don't want to track self-changes, 
                # but standard git commit -a is fine. Let's print changes.
                print("Changes detected:", flush=True)
                print(stdout, flush=True)
                
                # Git add
                print("Staging changes...", flush=True)
                add_code, _, add_err = run_command(["git", "add", "."])
                if add_code != 0:
                    print(f"Error running git add: {add_err}", flush=True)
                    time.sleep(10)
                    continue
                
                # Git commit
                print("Committing changes...", flush=True)
                commit_code, _, commit_err = run_command(["git", "commit", "-m", "Auto-sync LeetCode solution"])
                if commit_code != 0:
                    print(f"Error running git commit: {commit_err}", flush=True)
                    time.sleep(10)
                    continue
                
                # Git push
                print("Pushing to remote...", flush=True)
                push_code, _, push_err = run_command(["git", "push"])
                if push_code != 0:
                    print(f"Error running git push: {push_err}", flush=True)
                else:
                    print("Push successful!", flush=True)
            elif code != 0:
                print(f"Error checking git status: {stderr}", flush=True)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", flush=True)
        
        time.sleep(10)

if __name__ == "__main__":
    main()

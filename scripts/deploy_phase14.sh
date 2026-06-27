#!/bin/bash
# ZimaOS Deploy Script for Phase 14
# This script should be executed directly on the ZimaOS host (192.168.1.173)

echo "Starting ZimaOS Deploy for TokyoOS Phase 14..."

# Pull latest changes
git pull origin fusion-tokyo-openjarvis

# Setup and deploy
./setup-tokyo.sh

echo "Deployment triggered. Please check docker logs tokyoos -f to verify health."
echo "After deploying, run the validation script from your local machine:"
echo "python3 scripts/runtime_validate_phase_14_zimaos_real_deploy.py"

#!/bin/bash

# Trade Analytics App - Render.com Deployment Script
set -e

echo "🚀 Trade Analytics App - Render.com Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="trade-analytics"
RENDER_SERVICE_NAME="trade-analytics-dashboard"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   Repository: $REPO_NAME"
echo "   Service Name: $RENDER_SERVICE_NAME"
echo ""

# Step 1: Security Check
echo -e "${YELLOW}🔒 Running security check...${NC}"
python scripts/security-check.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Security check failed. Please fix issues before deploying.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Security check passed${NC}"

# Step 2: Check if git repository exists
echo -e "${YELLOW}🔍 Checking git repository...${NC}"
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📁 Initializing git repository...${NC}"
    git init
    git add .
    git commit -m "Initial commit: Trade Analytics Dashboard"
    echo -e "${GREEN}✅ Git repository initialized${NC}"
else
    echo -e "${GREEN}✅ Git repository exists${NC}"
fi

# Step 3: Check if remote exists
echo -e "${YELLOW}🔍 Checking remote repository...${NC}"
if ! git remote get-url origin > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  No remote repository configured.${NC}"
    echo -e "${BLUE}📝 Please create a GitHub repository and add it as remote:${NC}"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo "   git push -u origin main"
    echo ""
    echo -e "${BLUE}📝 Then follow these steps:${NC}"
    echo "   1. Go to https://render.com"
    echo "   2. Sign up/Login with GitHub"
    echo "   3. Click 'New +' → 'Web Service'"
    echo "   4. Connect your GitHub repository"
    echo "   5. Configure the service:"
    echo "      - Name: $RENDER_SERVICE_NAME"
    echo "      - Build Command: pip install -r requirements.txt"
    echo "      - Start Command: gunicorn --bind 0.0.0.0:\$PORT app:server"
    echo "   6. Click 'Create Web Service'"
    echo ""
    echo -e "${GREEN}✅ Deployment script completed${NC}"
    exit 0
else
    echo -e "${GREEN}✅ Remote repository configured${NC}"
fi

# Step 4: Push to GitHub
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
git add .
git commit -m "Update: Prepare for Render deployment" || echo "No changes to commit"
git push origin main
echo -e "${GREEN}✅ Pushed to GitHub${NC}"

# Step 5: Deployment instructions
echo ""
echo -e "${GREEN}🎉 Code is ready for Render deployment!${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "   1. Go to https://render.com"
echo "   2. Sign up/Login with GitHub"
echo "   3. Click 'New +' → 'Web Service'"
echo "   4. Connect your GitHub repository: $REPO_NAME"
echo "   5. Configure the service:"
echo "      - Name: $RENDER_SERVICE_NAME"
echo "      - Build Command: pip install -r requirements.txt"
echo "      - Start Command: gunicorn --bind 0.0.0.0:\$PORT app:server"
echo "      - Environment Variables (optional):"
echo "        * DEBUG=False"
echo "        * SECRET_KEY=your-secret-key-here"
echo "   6. Click 'Create Web Service'"
echo ""
echo -e "${BLUE}🌐 After deployment:${NC}"
echo "   - Your app will be available at: https://$RENDER_SERVICE_NAME.onrender.com"
echo "   - Update your website's REACT_APP_ANALYTICS_URL to point to this URL"
echo ""

echo -e "${GREEN}✅ Deployment script completed successfully!${NC}"



#!/bin/bash

# Deploy Analytics App to AWS App Runner
set -e

echo "🚀 Deploying Trade Analytics to AWS App Runner..."

# Configuration
SERVICE_NAME="trade-analytics"
REGION="us-east-2"
SOURCE_DIR="."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Service Name: $SERVICE_NAME"
echo "   Region: $REGION"
echo ""

# Check if service exists
if aws apprunner describe-service --service-name $SERVICE_NAME --region $REGION >/dev/null 2>&1; then
    echo -e "${YELLOW}🔄 Updating existing service...${NC}"
    
    # Get the service ARN
    SERVICE_ARN=$(aws apprunner describe-service --service-name $SERVICE_NAME --region $REGION --query 'Service.ServiceArn' --output text)
    
    # Create new deployment
    aws apprunner start-deployment --service-arn $SERVICE_ARN --region $REGION
    
    echo -e "${GREEN}✅ Deployment started for existing service${NC}"
else
    echo -e "${YELLOW}🆕 Creating new service...${NC}"
    
    # Create App Runner service
    aws apprunner create-service \
        --service-name $SERVICE_NAME \
        --region $REGION \
        --source-configuration '{
            "AutoDeploymentsEnabled": true,
            "AuthenticationConfiguration": {},
            "CodeRepository": {
                "CodeConfiguration": {
                    "ConfigurationSource": "API",
                    "Runtime": "PYTHON_3",
                    "BuildCommand": "pip install -r requirements.txt",
                    "StartCommand": "gunicorn --bind 0.0.0.0:8050 app:server",
                    "Port": "8050"
                },
                "SourceCodeVersion": {
                    "Type": "BRANCH",
                    "Value": "main"
                }
            }
        }' \
        --instance-configuration '{
            "Cpu": "1 vCPU",
            "Memory": "2 GB"
        }'
    
    echo -e "${GREEN}✅ New service created${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Analytics deployment initiated!${NC}"
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "   1. Wait for deployment to complete (check AWS Console)"
echo "   2. Get the service URL from App Runner console"
echo "   3. Update the website's analytics URL"
echo "   4. Test the analytics integration"
echo ""
echo -e "${YELLOW}🔗 Check status:${NC}"
echo "   aws apprunner describe-service --service-name $SERVICE_NAME --region $REGION"

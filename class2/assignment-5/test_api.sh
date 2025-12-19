#!/bin/bash

echo "Testing Blog API..."
echo ""

API_URL="http://localhost:5000"

echo "1. Health Check:"
curl -s $API_URL/health | python3 -m json.tool
echo ""

echo "2. API Info:"
curl -s $API_URL/ | python3 -m json.tool
echo ""

echo "3. Create Post 1:"
curl -s -X POST $API_URL/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Docker Deep Dive","content":"Learning Docker volumes and networks","author":"DevOps Student"}' \
  | python3 -m json.tool
echo ""

echo "4. Create Post 2:"
curl -s -X POST $API_URL/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Flask Best Practices","content":"Building REST APIs with Flask","author":"Python Developer"}' \
  | python3 -m json.tool
echo ""

echo "5. Get All Posts:"
curl -s $API_URL/posts | python3 -m json.tool
echo ""

echo "6. Get Single Post (ID=1):"
curl -s $API_URL/posts/1 | python3 -m json.tool
echo ""

echo "7. Database Stats:"
curl -s $API_URL/stats | python3 -m json.tool
echo ""

echo "Test completed!"


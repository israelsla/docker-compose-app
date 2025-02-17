#!/bin/bash

# שינוי מספר הרפליקות של האפליקציה
docker-compose scale app=$1

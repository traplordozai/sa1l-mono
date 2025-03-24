# Use official Node.js image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json + lock
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install
# Copy all app source
COPY . .

# Build the app
RUN npm run build

# Serve using Vite's preview
EXPOSE 4173
CMD ["npm", "run", "start"]
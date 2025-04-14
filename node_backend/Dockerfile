# Use an official Node.js image
FROM node:20

# Set the working directory inside container
WORKDIR /app

# Copy files into the container
COPY package*.json ./
RUN npm install
COPY . .

# Expose the port your app runs on
EXPOSE 3000

# Run the app
CMD ["node", "server.js"]

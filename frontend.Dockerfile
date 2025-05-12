# Use the official Nginx image as the base
FROM nginx:latest

# Copy static files to the Nginx HTML directory
COPY default.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for the frontend
EXPOSE 80

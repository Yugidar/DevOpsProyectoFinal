# Use the official Nginx image as the base
FROM nginx:latest

# Copy static files to the Nginx HTML directory
COPY ./templates /usr/share/nginx/html

# Expose port 80 for the frontend
EXPOSE 80

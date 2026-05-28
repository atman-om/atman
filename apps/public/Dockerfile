FROM node:22-alpine
WORKDIR /workspace/apps/public
COPY apps/public/package*.json ./
RUN npm install
COPY apps/public ./
EXPOSE 3001
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3001"]

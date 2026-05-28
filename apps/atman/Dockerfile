FROM node:20-alpine
WORKDIR /workspace/apps/atman
COPY apps/atman/package.json ./
RUN npm install
COPY apps/atman ./
EXPOSE 3002
CMD ["npm", "run", "dev"]

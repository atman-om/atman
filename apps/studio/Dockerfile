FROM node:20-alpine
WORKDIR /workspace/apps/studio
COPY apps/studio/package.json apps/studio/package-lock.json* ./
RUN npm install
COPY apps/studio ./
EXPOSE 3000
CMD ["npm", "run", "dev"]

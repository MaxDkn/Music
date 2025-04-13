FROM node:20

WORKDIR /app

RUN corepack enable && yarn set version stable

COPY package.json ./

RUN yarn install

COPY . .

EXPOSE 3000

CMD ["yarn", "dev"]

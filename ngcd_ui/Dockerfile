FROM node:6-slim as builder

RUN apt-get update && apt-get install libpng12-0

WORKDIR /reactapp

ADD package*.json ./
ADD yarn.lock ./
RUN ["npm", "install"]

ADD internals ./internals/
ADD server ./server/
ADD app ./app/
ADD .env.production ./
RUN ["npm", "run", "build"]

FROM nginx:stable-alpine as final

COPY app/.nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /reactapp/build /var/www/

EXPOSE 80

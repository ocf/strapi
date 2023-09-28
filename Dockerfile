# Creating multi-stage build for production
FROM node:18-alpine as strapi-production
RUN apk update && apk add --no-cache curl build-base gcc autoconf automake zlib-dev libpng-dev vips-dev > /dev/null 2>&1

ARG NODE_ENV=production
ENV NODE_ENV=${NODE_ENV}
ARG STRAPI_VERSION=v4.13.7
ENV STRAPI_VERSION=${STRAPI_VERSION}

WORKDIR /opt/app

RUN wget https://github.com/strapi/strapi/archive/refs/tags/${STRAPI_VERSION}.tar.gz \
  && tar -xzf ${STRAPI_VERSION}.tar.gz --strip-components=1 \
  && rm -f ${STRAPI_VERSION}.tar.gz \
  && yarn install
RUN yarn build

RUN chown -R node:node /opt/app
USER node
EXPOSE 1337
CMD ["yarn, "start"]

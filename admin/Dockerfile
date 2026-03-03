FROM node:20-alpine

ARG UID=1000
ARG GID=1000

# Create group and user (ignore errors if they already exist)
RUN addgroup -g ${GID} -S iproxy 2>/dev/null || true
RUN adduser -u ${UID} -G iproxy -s /bin/sh -D iproxy 2>/dev/null || true

WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER ${UID}
EXPOSE 3000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["npm", "run", "dev"]

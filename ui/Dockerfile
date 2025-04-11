FROM node:20

WORKDIR /app

# Installer Corepack et fixer la version stable de Yarn
RUN corepack enable && yarn set version stable

# Copier les fichiers source de l'application Next.js
COPY . .

# Installer les dépendances
RUN yarn install

# Exposer le port 3000 pour l'application Next.js
EXPOSE 3000

# Lancer l'application en mode développement
CMD ["yarn", "dev"]

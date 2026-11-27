const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'frontend/**/*.cy',
    supportFile: 'support/index.js',
  },
});
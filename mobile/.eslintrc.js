module.exports = {
  root: true,
  extends: ['@react-native-community'],
  parserOptions: {
    project: './tsconfig.json'
  },
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^ignored' }]
  }
};

require('dotenv').config({ path: '../.env' });

const app = require('./app');

const PORT = process.env.PORT || 4000;

app.listen(PORT, () => {
  console.log(`FixTrace-RAG backend listening on port ${PORT}`);
});

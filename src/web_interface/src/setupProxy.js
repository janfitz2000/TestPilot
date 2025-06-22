const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // AI Orchestrator API
  app.use(
    '/api/ai',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
      pathRewrite: {
        '^/api/ai': '',
      },
    })
  );

  // Instrument Gateway API
  app.use(
    '/api/instruments',
    createProxyMiddleware({
      target: 'http://localhost:8002',
      changeOrigin: true,
      pathRewrite: {
        '^/api/instruments': '',
      },
    })
  );

  // Workflow Engine API
  app.use(
    '/api/workflows',
    createProxyMiddleware({
      target: 'http://localhost:8003',
      changeOrigin: true,
      pathRewrite: {
        '^/api/workflows': '',
      },
    })
  );

  // Data Pipeline API
  app.use(
    '/api/data',
    createProxyMiddleware({
      target: 'http://localhost:8004',
      changeOrigin: true,
      pathRewrite: {
        '^/api/data': '',
      },
    })
  );
};
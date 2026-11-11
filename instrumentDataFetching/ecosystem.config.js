module.exports = {
  apps: [
    {
      name: "stream",
      script: "main.py",
      interpreter: "python3",           // or "/usr/bin/python3"
      args: "-dataTobeFetched=ohlcv.stream -debug-level=INFO",
      watch: false,                     // set to true if you want auto-restart on file change
      autorestart: false,
      max_restarts: 10,
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};

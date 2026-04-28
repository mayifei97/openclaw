const fs = require('fs');
const os = require('os');

const DATA_FILE = '/root/.openclaw/workspace/tools/sysmon_data.json';
const MAX_POINTS = 3600;

function readData() {
  try {
    const raw = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(raw);
  } catch { return { cpu: [], memory: [] }; }
}

function writeData(data) {
  if (data.cpu.length > MAX_POINTS) data.cpu = data.cpu.slice(-MAX_POINTS);
  if (data.memory.length > MAX_POINTS) data.memory = data.memory.slice(-MAX_POINTS);
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

function collect() {
  const cpus = os.loadavg();
  const cpuPct = Math.round((cpus[0] / os.cpus().length) * 100 * 100) / 100;
  const totalMemMB = Math.round(os.totalmem() / 1024 / 1024);
  const usedMemMB = Math.round((os.totalmem() - os.freemem()) / 1024 / 1024);
  const now = new Date().toISOString();

  const data = readData();
  data.cpu.push({ timestamp: now, value: cpuPct });
  data.memory.push({ timestamp: now, value: usedMemMB });
  writeData(data);
  console.log(`[${new Date().toISOString()}] cpu=${cpuPct}% mem=${usedMemMB}MB/${totalMemMB}MB`);
}

collect();
setInterval(collect, 1000); // 每 1 秒采集一次

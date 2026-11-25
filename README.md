# 旧物磅条（Scrapweigh）

骨架：过磅入站 → 品级锁价 → 结算关账 → 班次落印

- 前端 http://127.0.0.1:6700
- API http://127.0.0.1:11700
- 数据库环境变量 `SCRAPWEIGH_DB`（容器内默认 `/data/scrapweigh.db`）

```bash
docker compose up -d --build
```

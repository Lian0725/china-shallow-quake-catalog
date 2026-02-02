# 中国大陆浅源地震目录 (2015-2025)

基于多数据源的中国大陆浅源地震目录生成项目。

## 📊 数据概览

- **时间范围**: 2015-01-01 至 2025-12-31
- **震级范围**: 4.5 - 6.0 ML/mb/MS
- **深度范围**: 0 - 5 km (极浅源)
- **地理范围**: 中国大陆 (排除台湾、边境地区)
- **记录数量**: 137 条

## 📁 文件结构

```
seis_catalog/
├── fetch_quakes.py      # 数据获取脚本
├── plot_quakes.py       # 可视化脚本
├── china_quakes.csv     # 输出地震目录
├── china_quakes_map.png # 分布图
└── README.md            # 本文档
```

## 🌐 数据来源

| 数据源 | 说明 |
|--------|------|
| **ISC** | 国际地震中心 (含CENC/中国地震台网数据) |
| **EMSC** | 欧洲-地中海地震中心 |
| **USGS** | 美国地质调查局 |

数据来源参考了以下文献：
- Lei et al. (2017, 2019, 2021) 
- Wang et al. (2020, 2022)
- Zhao et al. (2023)

## 🚀 使用方法

### 安装依赖

```bash
pip install requests pandas matplotlib cartopy
```

### 运行数据获取

```bash
python fetch_quakes.py
```

### 生成分布图

```bash
python plot_quakes.py
```

## 📋 输出字段

| 字段 | 说明 |
|------|------|
| `id` | 事件唯一标识 |
| `time` | 发震时间 (UTC) |
| `latitude` | 纬度 |
| `longitude` | 经度 |
| `magnitude` | 震级 |
| `depth_km` | 震源深度 (km) |
| `place` | 地点描述 |
| `depth_method` | 深度测定方法 |
| `source` | 数据来源 |

## 📍 地震分布

| 地区 | 数量 |
|------|------|
| 新疆 | 78 |
| 西藏 | 26 |
| 四川 | 11 |
| 青海 | 7 |
| 云南 | 4 |
| 甘肃 | 1 |

## ⚠️ 过滤规则

1. **地理过滤**: 仅保留位置名称包含中国省份关键词的记录
2. **台湾排除**: 经纬度 (20-26.5°N, 118-123.5°E) 区域
3. **边境排除**: 任何包含 "BORDER" 或其他国家名称的记录
4. **去重规则**: 时间差 < 120秒 且 距离差 < 0.5° 视为重复

## 📖 参考文献

1. Lei, X., et al. (2017). Fault reactivation and earthquakes with magnitudes...
2. Lei, X., et al. (2019). The December 2018 ML 5.7 and January 2019 ML 5.3...
3. Lei, X., et al. (2021). Fluid-driven seismicity in relatively stable...
4. Wang, S., et al. (2020). InSAR Evidence Indicates a Link...
5. Wang, S., et al. (2022). Three Mw ≥ 4.7 Earthquakes Within the Changning...
6. Zhao, Y., et al. (2023). The 2021 Ms 6.0 Luxian (China) Earthquake...

## 📜 License

MIT License

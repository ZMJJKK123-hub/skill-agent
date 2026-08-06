# Tool: generate_gradle_config (Forge版)

## 用途
生成Forge项目的三个Gradle配置文件精确内容。

## 输入
```json
{
  "mc_version": "26.2",
  "forge_version": "65.1.0",
  "mod_id": "my_mod",
  "mod_group_id": "com.example.my_mod",
  "mappings_channel": "official"
}
```

## 输出
- build.gradle (完整)
- settings.gradle (完整)
- gradle.properties (完整)

# Tool: generate_language_entry

## 用途
生成翻译文件条目 (en_us.json + zh_cn.json)。

## 输入
```json
{
  "entries": [
    {
      "key": "block.mymod.my_block",
      "en": "Void Crystal Block",
      "zh": "虚空晶石块"
    },
    {
      "key": "item.mymod.my_item",
      "en": "Dragon Tooth",
      "zh": "龙牙"
    }
  ]
}
```

## 输出
- en_us.json 追加片段
- zh_cn.json 追加片段

# Minecraft MOD 骨架（最小可编译空壳占位）

此目录会被复制到每个用户的会话目录，作为 agent 生成 MOD 的起点。

当前为空骨架，agent 会在此目录下直接创建/修改文件来生成 MOD。
后续可在此放置一份最小可编译的空 MOD 工程（build.gradle + src 等），
让 agent 基于真实工程结构生成，产出物可直接构建。
